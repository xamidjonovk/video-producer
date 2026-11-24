import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MODES = ('auto', 'motion', 'cinematic', 'broll', 'iphone', 'repurpose')
PROFILES = {'reels': (1080, 1920), 'shorts': (1080, 1920), 'youtube': (1920, 1080)}
MEDIA_SUFFIXES = {'.mp4', '.mov', '.mkv', '.m4v', '.webm', '.avi', '.mts'}
LOCAL_SETTINGS = Path(__file__).resolve().with_name('studio.local.json')


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def command_path(name):
    configured = os.environ.get(f'VIDEO_AGENT_{name.upper()}')
    if not configured and LOCAL_SETTINGS.is_file():
        configured = load_json(LOCAL_SETTINGS).get(name)
    if configured:
        candidate = Path(configured).expanduser().resolve()
        return str(candidate) if candidate.is_file() else None
    found = shutil.which(name)
    if found:
        return found
    if name == 'ffmpeg':
        try:
            import imageio_ffmpeg
        except ImportError:
            return None
        return imageio_ffmpeg.get_ffmpeg_exe()
    return None


def run(executable, *args, cwd=None, checked=True):
    if not executable:
        raise ValueError('FFmpeg kerak. PATH yoki VIDEO_AGENT_FFMPEG orqali yo‘lini ko‘rsating.')
    result = subprocess.run(
        [executable, *map(str, args)], cwd=cwd, capture_output=True,
        encoding='utf-8', errors='replace', check=False,
    )
    if checked and result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip())
    return result


def ffmpeg(*args, cwd=None):
    return run(command_path('ffmpeg'), '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', *args, cwd=cwd)


def probe(path):
    executable = command_path('ffprobe')
    if executable:
        result = run(executable, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path)
        data = json.loads(result.stdout)
        streams = data.get('streams', [])
        video = next((stream for stream in streams if stream['codec_type'] == 'video'), {})
        rotation = next((side['rotation'] for side in video.get('side_data_list', []) if 'rotation' in side), 0)
        width, height = video.get('width'), video.get('height')
        if abs(rotation) % 180 == 90:
            width, height = height, width
        duration = data.get('format', {}).get('duration', 0)
        return {'duration': float(duration) if duration not in ('N/A', None) else 0,
                'audio': any(stream['codec_type'] == 'audio' for stream in streams),
                'width': width, 'height': height, 'video': video}
    result = run(command_path('ffmpeg'), '-hide_banner', '-i', path, checked=False)
    info = result.stderr
    duration = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', info)
    video = next((line for line in info.splitlines() if 'Video:' in line), '')
    dimensions = re.search(r'\b(\d{2,5})x(\d{2,5})\b', video)
    width, height = (int(dimensions[1]), int(dimensions[2])) if dimensions else (None, None)
    rotated = re.search(r'rotation of (-?[\d.]+) degrees', info)
    if rotated and abs(float(rotated[1])) % 180 == 90:
        width, height = height, width
    return {
        'duration': int(duration[1]) * 3600 + int(duration[2]) * 60 + float(duration[3]) if duration else 0,
        'audio': 'Audio:' in info, 'width': width, 'height': height, 'video': video.strip(),
    }


def init(args):
    args.job.mkdir(parents=True, exist_ok=True)
    for name in ('assets', 'inspection', 'exports'):
        (args.job / name).mkdir(exist_ok=True)
    for name, data in {
        'brief.json': {'mode': args.mode, 'platform': args.profile, 'language': 'uz', 'goal': ''},
        'script.json': {'hook': '', 'scenes': []},
        'edit.json': {'profile': args.profile, 'fps': 30, 'clips': [], 'audio': [], 'subtitles': None},
    }.items():
        path = args.job / name
        if not path.exists():
            save_json(path, data)
    print(args.job.resolve())


def doctor(_args):
    print(json.dumps({name: command_path(name) for name in ('ffmpeg', 'ffprobe', 'node', 'nvidia-smi')}, indent=2))


def media_path(job, value):
    path = (job / value).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError(f'Media fayl kerak: {path}')
    return path


def inspect(args):
    source = args.source.resolve(strict=True)
    if source.suffix.lower() not in MEDIA_SUFFIXES:
        raise ValueError(f'Video turi: {source.suffix}')
    info = probe(source)
    if not info['width'] or not info['duration']:
        raise ValueError(f'Video davomiyligi va kadr o‘lchamini aniqlab bo‘lmadi: {source}')
    out = args.job / 'inspection' / args.slug
    out.mkdir(parents=True, exist_ok=True)
    save_json(out / 'media.json', {'source': str(source), **info})
    if info['audio']:
        ffmpeg('-i', source, '-vn', '-ac', '1', '-ar', '16000', out / 'speech.wav')
    interval = info['duration'] / 12
    ffmpeg('-ss', f'{interval / 2:.6f}', '-i', source,
           '-vf', f'fps=1/{interval:.6f}:round=near,scale=320:180:force_original_aspect_ratio=decrease,'
           'pad=320:180:(ow-iw)/2:(oh-ih)/2,tile=3x4:nb_frames=10',
           '-frames:v', '1', '-update', '1', out / 'frames.jpg')
    if not (out / 'frames.jpg').is_file():
        raise ValueError(f'Kadrlar varag‘ini yaratib bo‘lmadi: {source.name}')
    print(out.resolve())


def number(value, name, low=0, high=86400):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} uchun son kerak.')
    if not low <= value <= high:
        raise ValueError(f'{name} {low} va {high} oralig‘ida bo‘lishi kerak.')
    return float(value)


def geometry(width, height, fit):
    if fit == 'fill':
        return (f'scale={width}:{height}:force_original_aspect_ratio=increase:force_divisible_by=2,'
                f'crop={width}:{height}')
    if fit == 'fit':
        return (f'scale={width}:{height}:force_original_aspect_ratio=decrease:force_divisible_by=2,'
                f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2')
    raise ValueError('clip.fit qiymati fit yoki fill bo‘lsin.')


def clean(args):
    job = args.job.resolve()
    source = args.source.resolve(strict=True)
    plan = load_json(job / 'edit.json')
    info = probe(source)
    if not info['width'] or not info['audio'] or not info['duration']:
        raise ValueError('Pauzalarni izlash uchun audio va video oqimi kerak.')
    minimum = number(args.min_pause, 'min-pause', 0.1, 30)
    keep = number(args.keep_pause, 'keep-pause', 0, minimum)
    noise = number(args.noise_db, 'noise-db', -90, -6)
    fps = number(plan.get('fps', 30), 'fps', 15, 60)
    detected = run(command_path('ffmpeg'), '-nostdin', '-hide_banner', '-i', source,
                   '-vn', '-af', f'silencedetect=noise={noise:g}dB:d={minimum:g}', '-f', 'null', '-')
    pattern = r'silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)'
    clips = []
    removals = []
    cursor = 0.0
    for end_text, length_text in re.findall(pattern, detected.stderr):
        end = min(float(end_text), info['duration'])
        start = max(0.0, end - float(length_text))
        cut_start = start if start < 1 / fps else start + keep / 2
        cut_end = end if info['duration'] - end < 1 / fps else end - keep / 2
        if cut_end - cut_start < 1 / fps:
            continue
        if cut_start - cursor >= 1 / fps:
            clips.append({'file': str(source), 'start': cursor, 'end': cut_start})
        removals.append({'start': cut_start, 'end': cut_end})
        cursor = cut_end
    if info['duration'] - cursor >= 1 / fps:
        clips.append({'file': str(source), 'start': cursor, 'end': info['duration']})
    if not clips or sum(clip['end'] - clip['start'] for clip in clips) < 1:
        raise ValueError('Saqlash uchun yetarli ovoz aniqlanmadi. Audio va noise-db qiymatini tekshiring.')
    save_json(job / 'clean-edit.json', {'profile': plan['profile'], 'fps': fps,
              'clips': clips, 'audio': [], 'subtitles': None})
    save_json(job / 'pause-review.json', {'source': str(source), 'removed_ranges_seconds': removals})
    print(job / 'clean-edit.json')


def normalize_clip(job, clip, fps, size, destination):
    path = media_path(job, clip['file'])
    meta = probe(path)
    if not meta['width'] or not meta['duration']:
        raise ValueError(f'Video manbasi tekshiruvdan o‘tmadi: {path}')
    details = json.dumps(meta['video']).lower()
    if any(value in details for value in ('smpte2084', 'arib-std-b67', 'dolby vision', 'dovi configuration')):
        raise ValueError(f'HDR manba uchun Resolve’da SDR proksi tayyorlang: {path}')
    start = number(clip.get('start', 0), 'clip.start')
    end = number(clip.get('end', meta['duration']), 'clip.end')
    if end <= start or end > meta['duration'] + 0.04:
        raise ValueError(f'Kesim media chegarasidan tashqarida: {path.name}, {start:g}–{end:g}s')
    frames = round((min(end, meta['duration']) - start) * fps)
    if frames < 1:
        raise ValueError(f'Kesim bir kadrdan qisqa: {path.name}')
    duration = frames / fps
    gain = number(clip.get('gain', 1), 'clip.gain', 0, 4)
    video_filter = f'{geometry(*size, clip.get("fit", "fit"))},setsar=1,fps={fps},tpad=stop_mode=clone:stop_duration=1'
    inputs = ['-ss', f'{start:.6f}', '-i', path]
    audio_map = '0:a:0'
    if not meta['audio'] or gain == 0:
        inputs += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
        audio_map = '1:a:0'
    ffmpeg(*inputs, '-map', '0:v:0', '-map', audio_map, '-t', f'{duration:.8f}',
           '-vf', video_filter, '-af', f'volume={gain:g},apad',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p',
           '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', destination)
    return duration


def assemble(job, plan, stage, output, duration):
    filters = []
    inputs = ['-f', 'concat', '-safe', '1', '-i', 'clips.txt']
    count = 1
    for index, track in enumerate(plan.get('audio', []), 1):
        start = number(track.get('start', 0), 'audio.start')
        seconds = number(track.get('duration', duration - start), 'audio.duration', 0.001)
        gain = number(track.get('gain', 0.18), 'audio.gain', 0, 4)
        if start >= duration:
            raise ValueError('Audio treki video tugaganidan keyin boshlanmoqda.')
        if track.get('loop', False):
            inputs += ['-stream_loop', '-1']
        inputs += ['-i', media_path(job, track['file'])]
        filters.append(f'[{index}:a]aresample=48000,aformat=channel_layouts=stereo,'
                       f'atrim=duration={min(seconds, duration - start):.6f},asetpts=PTS-STARTPTS,'
                       f'volume={gain:g},adelay={round(start * 1000)}:all=1[a{index}]')
        count += 1
    audio_map = '0:a:0'
    if filters:
        labels = ''.join(f'[a{index}]' for index in range(1, count))
        filters.append(f'[0:a]{labels}amix=inputs={count}:duration=first:normalize=0,'
                       'alimiter=limit=0.95:level=false:latency=1[aout]')
        audio_map = '[aout]'
    audio_args = ['-c:a', 'aac', '-b:a', '192k']
    if filters:
        audio_args += ['-filter_complex', ';'.join(filters)]
    video_args = ['-c:v', 'copy']
    if plan.get('subtitles'):
        source = media_path(job, plan['subtitles'])
        if source.suffix.lower() != '.srt':
            raise ValueError('edit.json subtitri SRT formatida bo‘lishi kerak.')
        shutil.copyfile(source, stage / 'captions.srt')
        style = 'FontName=Arial,FontSize=17,Outline=2,Shadow=0,Alignment=2,MarginV=45'
        video_args = ['-vf', f"subtitles=filename=captions.srt:force_style='{style}'", '-c:v', 'libx264',
                      '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p']
    ffmpeg(*inputs, '-map', '0:v:0', *audio_args, '-map', audio_map, *video_args,
           '-t', f'{duration:.8f}', '-movflags', '+faststart', output, cwd=stage)


def render(args):
    job = args.job.resolve()
    plan = load_json(media_path(job, args.plan))
    profile = plan['profile']
    if profile not in PROFILES:
        raise ValueError(f'Noma’lum profil: {profile}')
    fps = number(plan.get('fps', 30), 'fps', 15, 60)
    if not plan['clips']:
        raise ValueError('edit.json ichida kamida bitta video kesimi kerak.')
    exports = job / 'exports'
    exports.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='render-', dir=exports) as directory:
        stage = Path(directory)
        names = [f'clip-{index:04}.mov' for index in range(len(plan['clips']))]
        duration = sum(normalize_clip(job, clip, fps, PROFILES[profile], stage / name)
                       for clip, name in zip(plan['clips'], names, strict=True))
        (stage / 'clips.txt').write_text(''.join(f"file '{name}'\n" for name in names), encoding='ascii')
        output = stage / 'final.mp4'
        assemble(job, plan, stage, output, duration)
        result = probe(output)
        if (result['width'], result['height']) != PROFILES[profile] or not result['audio']:
            raise ValueError('Eksportning kadr o‘lchami yoki audio oqimi mos kelmadi.')
        if abs(result['duration'] - duration) > 0.18:
            raise ValueError(f'Eksport davomiyligi mos kelmadi: {result["duration"]:.3f}s / {duration:.3f}s')
        ffmpeg('-xerror', '-i', output, '-f', 'null', '-')
        result['technical_check'] = 'decoded'
        result['editorial_review'] = 'pending'
        save_json(stage / 'technical-review.json', result)
        output.replace(exports / 'final.mp4')
        (stage / 'technical-review.json').replace(exports / 'technical-review.json')
    print(exports / 'final.mp4')


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def draft(args):
    job = args.job.resolve()
    video = media_path(job, str(args.video) if args.video else 'exports/final.mp4')
    caption_path = media_path(job, 'caption.txt')
    caption = caption_path.read_text(encoding='utf-8-sig').strip()
    if not caption or video.suffix.lower() != '.mp4':
        raise ValueError('Post uchun bo‘sh bo‘lmagan caption.txt va MP4 kerak.')
    info = probe(video)
    if not info['audio'] or not info['duration'] or not info['width'] or not info['height']:
        raise ValueError('Nashr faylida tekshiriladigan audio va video kerak.')
    if args.platform == 'instagram':
        if info['height'] <= info['width']:
            raise ValueError('Bu ish oqimidagi Instagram Reels uchun vertikal MP4 kerak.')
        if not 3 <= info['duration'] <= 900:
            raise ValueError('Instagram Reel nashri uchun video 3 soniyadan 15 daqiqagacha bo‘lishi kerak.')
    cover = media_path(job, str(args.cover)) if args.cover else None
    package = {'platform': args.platform, 'account': args.account, 'title': args.title,
               'video': str(video), 'video_sha256': sha256(video), 'caption': caption,
               'cover': str(cover) if cover else None, 'cover_sha256': sha256(cover) if cover else None,
               'status': 'local_draft', 'duration': info['duration'],
               'size': [info['width'], info['height']]}
    save_json(job / 'publish-draft.json', package)
    print(job / 'publish-draft.json')


def slug(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}', value):
        raise argparse.ArgumentTypeError('Nom uchun lotin harfi, raqam, - yoki _ ishlating.')
    return value


def main():
    parser = argparse.ArgumentParser(description='Lokal video kontent ishlari')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('doctor').set_defaults(action=doctor)
    init_cmd = commands.add_parser('init')
    init_cmd.add_argument('job', type=Path)
    init_cmd.add_argument('--mode', choices=MODES, default='auto')
    init_cmd.add_argument('--profile', choices=PROFILES, default='reels')
    init_cmd.set_defaults(action=init)
    inspect_cmd = commands.add_parser('inspect')
    inspect_cmd.add_argument('job', type=Path)
    inspect_cmd.add_argument('source', type=Path)
    inspect_cmd.add_argument('--slug', type=slug, default='source')
    inspect_cmd.set_defaults(action=inspect)
    render_cmd = commands.add_parser('render')
    render_cmd.add_argument('job', type=Path)
    render_cmd.add_argument('--plan', default='edit.json')
    render_cmd.set_defaults(action=render)
    clean_cmd = commands.add_parser('clean')
    clean_cmd.add_argument('job', type=Path)
    clean_cmd.add_argument('source', type=Path)
    clean_cmd.add_argument('--min-pause', type=float, default=0.75)
    clean_cmd.add_argument('--keep-pause', type=float, default=0.28)
    clean_cmd.add_argument('--noise-db', type=float, default=-38)
    clean_cmd.set_defaults(action=clean)
    draft_cmd = commands.add_parser('draft')
    draft_cmd.add_argument('job', type=Path)
    draft_cmd.add_argument('--platform', choices=('instagram', 'youtube'), default='instagram')
    draft_cmd.add_argument('--account')
    draft_cmd.add_argument('--title')
    draft_cmd.add_argument('--video', type=Path)
    draft_cmd.add_argument('--cover', type=Path)
    draft_cmd.set_defaults(action=draft)
    args = parser.parse_args()
    try:
        args.action(args)
    except (KeyError, OSError, ValueError, TypeError) as error:
        print(f'Xato: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
