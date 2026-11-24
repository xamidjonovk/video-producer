"""Install the shared skill when the host marketplace is unavailable."""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


SKILL = Path(__file__).resolve().parent / "plugins/video-producer/skills/video-producer"
HOSTS = {"codex": ".agents", "claude": ".claude"}
COMPANION = SKILL.with_name("higgsfield-shots")


def check_target(directory, skill):
    target = directory / skill.name
    if target.exists() or target.is_symlink():
        for source in skill.rglob("*"):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            installed = target / source.relative_to(skill)
            if not installed.is_file() or installed.read_bytes() != source.read_bytes():
                raise ValueError(f"Existing skill differs: {target}. Back it up before replacing it.")
    return target


def install(directory, skill=SKILL):
    target = check_target(directory, skill)
    if target.exists():
        return target
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="video-producer-install-", dir=directory) as temporary:
        staged = Path(temporary) / skill.name
        shutil.copytree(skill, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        staged.rename(target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", choices=(*HOSTS, "both"))
    parser.add_argument("--project", type=Path, help="Install into this project instead of the user profile.")
    args = parser.parse_args()
    hosts = HOSTS if args.host == "both" else (args.host,)
    try:
        base = args.project.resolve(strict=True) if args.project else Path.home()
        if not base.is_dir():
            raise ValueError(f"Expected a directory: {base}")
        targets = [(base / HOSTS[host] / "skills", skill) for host in hosts for skill in (SKILL, COMPANION)]
        for directory, skill in targets:
            check_target(directory, skill)
        for directory, skill in targets:
            print(install(directory, skill))
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
