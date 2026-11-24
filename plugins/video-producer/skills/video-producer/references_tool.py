import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import parse_qs, urlencode, urlsplit

from studio import MEDIA_SUFFIXES, inspect, load_json, sha256


REFERENCE_SUFFIXES = MEDIA_SUFFIXES | {'.png', '.jpg', '.jpeg', '.webp', '.wav', '.mp3', '.m4a', '.flac', '.pdf'}
YOUTUBE_ID = re.compile(r'[\w-]{11}', re.ASCII)
INSTAGRAM_ID = re.compile(r'[A-Za-z0-9_.-]{1,64}')


def canonical_url(raw):
    parts = urlsplit(raw.strip())
    if parts.scheme not in ('https', 'http') or parts.username or parts.password:
        raise ValueError('Enter a public Instagram or YouTube URL.')
    host = parts.hostname
    segments = [value for value in parts.path.split('/') if value]
    first = segments[0] if segments else ''
    youtube = ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com')
    if host == 'youtu.be' or host in youtube:
        video = first if host == 'youtu.be' else parse_qs(parts.query).get('v', [''])[0]
        if first in ('shorts', 'live', 'embed') and len(segments) == 2:
            video = segments[1]
        if YOUTUBE_ID.fullmatch(video):
            return 'https://www.youtube.com/watch?' + urlencode({'v': video})
        if host in youtube and (re.fullmatch(r'@[\w.-]+', first) or
                                (first in ('channel', 'c', 'user') and len(segments) in (2, 3) and
                                 re.fullmatch(r'[\w.-]+', segments[1]))):
            return 'https://www.youtube.com/' + '/'.join(segments[:1 if first.startswith('@') else 2])
    if host in ('instagram.com', 'www.instagram.com', 'm.instagram.com'):
        if first in ('p', 'reel', 'reels', 'tv') and len(segments) == 2 and INSTAGRAM_ID.fullmatch(segments[1]):
            route = 'reel' if first == 'reels' else first
            return f'https://www.instagram.com/{route}/{segments[1]}/'
        if (len(segments) == 1 or len(segments) == 2 and segments[1] == 'reels') and re.fullmatch(r'[A-Za-z0-9_.]{1,30}', first) and first not in (
                'accounts', 'explore', 'reels', 'reel', 'p', 'tv', 'direct', 'about'):
            return f'https://www.instagram.com/{first}/'
    raise ValueError('Unsupported link. Use a public Reel, post, profile, YouTube video or channel URL.')


def directory(path, root):
    if path.resolve().is_relative_to(root):
        path.mkdir(parents=True, exist_ok=True)
        return path
    raise ValueError(f'Reference location is outside the project: {path}')


def write_index(path, index):
    with NamedTemporaryFile(dir=path.parent, delete=False, mode='w', encoding='utf-8') as handle:
        temporary = Path(handle.name)
        json.dump(index, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def record(root, items, source):
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    if isinstance(source, str):
        url = canonical_url(source)
        key = 'url-' + hashlib.sha256(url.encode()).hexdigest()[:16]
        new = {'kind': 'url', 'url': url, 'access': 'pending'}
        if '/shorts/' in urlsplit(source).path and 'youtube.com' in urlsplit(url).netloc:
            new['format'] = 'shorts'
    else:
        if source.suffix.lower() not in REFERENCE_SUFFIXES:
            raise ValueError(f'Unsupported reference file: {source.name}')
        digest = sha256(source)
        key = 'file-' + digest[:16]
        existing = items.get(key, {})
        prior = (root / existing.get('path', '')).resolve()
        if prior.is_file() and prior.is_relative_to(root.resolve()):
            return key
        chosen = source
        if not source.is_relative_to(root.resolve()):
            media = directory(root / 'media', root.resolve())
            chosen = media / f'{key}{source.suffix.lower()}'
            if chosen.is_symlink():
                raise ValueError(f'Unsafe reference file destination: {chosen}')
            if not chosen.exists():
                with NamedTemporaryFile(dir=media, delete=False) as output:
                    temporary = Path(output.name)
                try:
                    shutil.copyfile(source, temporary)
                    temporary.replace(chosen)
                finally:
                    temporary.unlink(missing_ok=True)
        new = {'kind': 'file', 'path': chosen.relative_to(root).as_posix(),
               'name': source.name, 'sha256': digest, 'access': 'local'}
    items.setdefault(key, {'id': key, 'added_at': now, 'notes': f'notes/{key}.md'}).update(
        {field: value for field, value in new.items() if field != 'access' or 'access' not in items.get(key, {})})
    return key


def process(args, emit=True):
    project = args.project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError('The project must be a directory.')
    root = directory(project / 'references', project)
    notes = directory(root / 'notes', root)
    directory(root / 'inspection', root)
    index_path = root / 'index.json'
    if index_path.is_symlink():
        raise ValueError('Reference index is a symlink.')
    index = load_json(index_path) if index_path.exists() else {'version': 1, 'items': {}}
    items = index['items']
    sources = []
    if args.command == 'sync':
        for file in sorted(root.rglob('*')):
            if file.relative_to(root).parts[0] in ('notes', 'inspection') or file.is_symlink():
                continue
            if file.is_file() and file.suffix.lower() in REFERENCE_SUFFIXES and file.resolve().is_relative_to(root):
                sources.append(file)
    else:
        for source in args.sources:
            if re.match(r'https?://', source, re.IGNORECASE):
                sources.append(source)
            else:
                file = (project / source).expanduser().resolve(strict=True)
                if not file.is_file():
                    raise ValueError(f'Expected a reference file: {file}')
                sources.append(file)
    keys = list(dict.fromkeys(record(root, items, source) for source in sources))
    write_index(index_path, index)
    for key in keys:
        entry = items[key]
        if entry['kind'] == 'url':
            note = notes / f'{key}.md'
            try:
                with note.open('x', encoding='utf-8') as file:
                    file.write(f"# Video reference\n\n{entry['url']}\n\nAnalysis pending.\n")
            except FileExistsError:
                pass
    result = [items[key] for key in keys]
    if emit:
        print(json.dumps({'index': str(index_path), 'references': result}, ensure_ascii=False))
    if args.inspect:
        for key in keys:
            entry = items[key]
            if entry['kind'] != 'file':
                continue
            source = (root / entry['path']).resolve(strict=True)
            if source.suffix.lower() in MEDIA_SUFFIXES and source.is_relative_to(root):
                directory(root / 'inspection' / key, root)
                inspect(argparse.Namespace(job=root, source=source, slug=key))
    return result


def main():
    parser = argparse.ArgumentParser(description='Store and index video references inside a project.')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('add', 'sync'):
        command = commands.add_parser(name)
        command.add_argument('project', type=Path)
        command.add_argument('--inspect', action='store_true')
        if name == 'add':
            command.add_argument('sources', nargs='+')
    try:
        process(parser.parse_args())
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
