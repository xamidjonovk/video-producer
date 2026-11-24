"""Read a bounded sample of public video metadata and retrieve authorized clips."""

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from references_tool import canonical_url, directory, process
from studio import MEDIA_SUFFIXES, run, save_json


def video_url(url):
    parsed = urlsplit(url)
    return parsed.path == '/watch' or parsed.path.startswith(('/reel/', '/p/', '/tv/'))


def summary(item):
    keys = ('id', 'title', 'duration', 'view_count', 'like_count', 'upload_date', 'timestamp',
            'channel', 'uploader', 'description', 'availability')
    result = {key: item[key] for key in keys if item.get(key) is not None}
    for key in ('webpage_url', 'url'):
        try:
            url = canonical_url(item.get(key) or '')
        except ValueError:
            continue
        result['url'] = url
        break
    if 'description' in result:
        result['description'] = result['description'][:1500]
    return result


def collect(project, url, limit, downloader, download=False, encoder=None, brief=False):
    project = project.resolve(strict=True)
    supplied_url = url
    original_path = urlsplit(url).path.rstrip('/')
    url = canonical_url(url)
    single = video_url(url)
    if download and not single:
        raise ValueError('Use a single authorized video URL for media retrieval.')
    if not 1 <= limit <= 30:
        raise ValueError('Use a sample size from 1 to 30.')
    source = url
    sample = 'media' if download else 'video' if single else 'profile'
    if not single and urlsplit(url).hostname == 'www.youtube.com':
        sample = 'shorts' if original_path.endswith('/shorts') else 'videos'
        source = f'{url.rstrip("/")}/{sample}'
    root = directory(project / 'references', project)
    reports = directory(root / 'online', root.resolve())
    reference = process(argparse.Namespace(project=project, command='add', sources=[supplied_url], inspect=False),
                        emit=False)[0]
    command = [*downloader[1:], '--ignore-config', '--no-progress',
               '--socket-timeout', '12', '--retries', '1', '--extractor-retries', '1']
    if shutil.which('node'):
        command += ['--js-runtimes', 'node']
    options = ['--no-playlist'] if single else ['--flat-playlist', '--playlist-end', str(limit)]
    report = {'source': url, 'queried_url': source, 'sample_limit': 1 if single else limit,
              'collected_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'evidence': 'metadata', 'access': 'unavailable', 'videos': []}
    report_path = reports / f'{reference["id"]}-{sample}.json'
    metadata = run(downloader[0], *command, *options, '--skip-download', '--dump-single-json', '--', source,
                   checked=False)
    if metadata.returncode or not metadata.stdout.strip():
        report['provider_message'] = metadata.stderr.strip()[-1500:]
    else:
        data = json.loads(metadata.stdout)
        videos = [item for item in data.get('entries', [data]) if item][:limit]
        report['videos'] = [summary(item) for item in videos]
        report['access'] = 'available' if videos else 'no_visible_videos'
    save_json(report_path, report)
    if download and report['access'] == 'available':
        with tempfile.TemporaryDirectory(prefix='video-source-', dir=reports) as temporary:
            args = ['--no-playlist', '--max-filesize', '100M', '--output', str(Path(temporary) / '%(id)s.%(ext)s'),
                    '--format', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]/b' if encoder
                    else 'b[height<=1080]/b']
            if encoder:
                args += ['--ffmpeg-location', str(encoder), '--merge-output-format', 'mp4']
            try:
                run(downloader[0], *command, *args, '--', source)
                clips = [p for p in Path(temporary).iterdir() if p.suffix.lower() in MEDIA_SUFFIXES]
                if len(clips) != 1:
                    raise ValueError('The provider returned no complete supported clip within the size limit.')
                entry = process(argparse.Namespace(project=project, command='add', sources=[str(clips[0])],
                                                   inspect=False), emit=False)[0]
                report.update(evidence='downloaded_media', local_reference=entry)
            except ValueError as error:
                report['download_error'] = str(error)[-1500:]
        save_json(report_path, report)
    receipt = {'report': str(report_path), **report}
    if brief:
        receipt['videos'] = [{key: item[key] for key in ('id', 'title', 'duration', 'view_count', 'url') if key in item}
                             for item in report['videos']]
    print(json.dumps(receipt, ensure_ascii=False))
    return 0 if report['access'] == 'available' and 'download_error' not in report else 2
