"""Check local capabilities and prepare only the video engine selected for a job."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from routing import WORKFLOWS, production_plan
from studio import command_path


SKILL = Path(__file__).resolve().parent
HYPERFRAMES_VERSION = "0.9.86"
FFMPEG_FALLBACK = "imageio-ffmpeg==0.6.0"
TRANSCRIBER = "faster-whisper==1.2.1"
PACKAGES = {"hyperframes": "hyperframes", "remotion": "@remotion/cli"}


def runtime(project):
    location = project / ".video-producer"
    if not location.resolve().is_relative_to(project):
        raise ValueError(f"Runtime directory resolves outside the project: {location}")
    return location


def local_python(project):
    environment = runtime(project) / "venv"
    return environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def ffmpeg(project):
    found = command_path("ffmpeg")
    if found:
        return found
    executable = local_python(project)
    if executable.is_file():
        result = subprocess.run(
            [str(executable), "-c", "from imageio_ffmpeg import get_ffmpeg_exe; print(get_ffmpeg_exe())"],
            text=True, capture_output=True, check=False,
        )
        path = result.stdout.strip()
        if result.returncode == 0 and Path(path).is_file():
            return path
    return None


def install_python_package(project, package):
    executable = local_python(project)
    if not executable.is_file():
        subprocess.run([sys.executable, "-m", "venv", str(runtime(project) / "venv")], check=True)
    subprocess.run([str(executable), "-m", "pip", "install", "--disable-pip-version-check",
                    "--only-binary=:all:", package], check=True)


def transcriber_ready(project):
    executable = local_python(project)
    if not executable.is_file():
        return False
    result = subprocess.run([str(executable), "-c", "from faster_whisper import WhisperModel"],
                            capture_output=True, check=False)
    return result.returncode == 0


def prepare_ffmpeg(project):
    if not ffmpeg(project):
        install_python_package(project, FFMPEG_FALLBACK)
    path = ffmpeg(project)
    if not path:
        raise ValueError("FFmpeg is still unavailable. Install an FFmpeg build on PATH or set VIDEO_AGENT_FFMPEG.")
    return path


def npm_command():
    node = shutil.which("node")
    npm = shutil.which("npm")
    if not node or not npm:
        raise ValueError("Install Node.js 22+ with npm to prepare a motion renderer.")
    version = subprocess.check_output([node, "--version"], text=True).strip()
    if int(version.removeprefix("v").split(".", 1)[0]) < 22:
        raise ValueError(f"Motion renderers need Node.js 22 or newer. Found {version}.")
    npm_path = Path(npm)
    if os.name == "nt":
        entry = npm_path.parent / "node_modules/npm/bin/npm-cli.js"
        if not entry.is_file():
            raise ValueError(f"Could not find npm-cli.js beside {npm}. Use a standard Node.js installation.")
        return [node, str(entry)]
    return [npm]


def engine_directory(project, engine):
    directory = (project / "remotion") if engine == "remotion" else (runtime(project) / engine)
    if not directory.resolve().is_relative_to(project):
        raise ValueError(f"Engine directory resolves outside the project: {directory}")
    return directory


def engine_bin(directory, engine):
    package = directory / "node_modules" / PACKAGES[engine]
    manifest = package / "package.json"
    if not manifest.is_file():
        return None
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    command = metadata["bin"]
    target = (package / (command if isinstance(command, str) else command[engine])).resolve()
    if target.is_relative_to(package.resolve()) and target.is_file():
        return target
    return None


def prepare_renderer(project, engine):
    command = npm_command()
    directory = engine_directory(project, engine)
    package = directory / "package.json"
    if not package.is_file():
        if directory.exists() and any(directory.iterdir()):
            raise ValueError(f"Choose a clean project folder or use the existing project at {directory}.")
        directory.mkdir(parents=True, exist_ok=True)
        if engine == "hyperframes":
            metadata = {"private": True, "dependencies": {"hyperframes": HYPERFRAMES_VERSION}}
            with package.open("x", encoding="utf-8") as handle:
                json.dump(metadata, handle, indent=2)
        else:
            template = SKILL / "templates/remotion"
            shutil.copytree(template, directory, dirs_exist_ok=True)
    if not engine_bin(directory, engine):
        install_mode = "ci" if (directory / "package-lock.json").is_file() else "install"
        subprocess.run([*command, install_mode, "--no-audit", "--no-fund"], cwd=directory, check=True)
    if not engine_bin(directory, engine):
        raise ValueError(f"{engine} is unavailable in {directory}. Inspect its npm install output.")
    return directory


def studio_environment(project):
    environment = os.environ.copy()
    detected = ffmpeg(project)
    if detected:
        environment["VIDEO_AGENT_FFMPEG"] = detected
    return environment


def run_engine(project, engine, arguments):
    directory = engine_directory(project, engine)
    command = engine_bin(directory, engine)
    node = shutil.which("node")
    if not command or not node:
        raise ValueError(f"Run prepare for {engine} in this project first.")
    environment = studio_environment(project)
    if engine == "hyperframes":
        encoder = environment.get("VIDEO_AGENT_FFMPEG")
        if not encoder:
            raise ValueError("Prepare FFmpeg for this project before using HyperFrames.")
        if not shutil.which("ffmpeg"):
            bin_directory = runtime(project) / "bin"
            bin_directory.mkdir(exist_ok=True)
            alias = bin_directory / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if not alias.exists():
                shutil.copy2(encoder, alias)
            environment["PATH"] = str(bin_directory) + os.pathsep + environment.get("PATH", "")
    return subprocess.call([node, str(command), *arguments], cwd=directory if engine == "remotion" else project,
                           env=environment)


def doctor(project):
    print(json.dumps({
        "project": str(project),
        "python": sys.version.split()[0],
        "ffmpeg": ffmpeg(project),
        "ffprobe": command_path("ffprobe"),
        "node": shutil.which("node"),
        "npm": shutil.which("npm"),
        "hyperframes_ready": engine_bin(engine_directory(project, "hyperframes"), "hyperframes") is not None,
        "remotion_ready": engine_bin(engine_directory(project, "remotion"), "remotion") is not None,
        "effectcraft_cli": shutil.which("effectcraft-cli"),
        "transcriber_ready": transcriber_ready(project),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "plan", "prepare", "studio", "engine", "transcribe"):
        command = commands.add_parser(name)
        command.add_argument("project", type=Path)
        if name == "prepare":
            command.add_argument("engine", choices=("ffmpeg", "transcription", *PACKAGES))
        if name == "plan":
            command.add_argument("workflows", choices=WORKFLOWS, nargs="+")
        if name == "engine":
            command.add_argument("engine", choices=PACKAGES)
        if name in ("engine", "studio", "transcribe"):
            command.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        project = args.project.resolve(strict=True)
        if not project.is_dir():
            raise ValueError(f"Expected a project directory: {project}")
        if args.command == "doctor":
            doctor(project)
        elif args.command == "plan":
            print(json.dumps(production_plan(args.workflows), indent=2))
        elif args.command == "prepare":
            if args.engine == "ffmpeg":
                print(prepare_ffmpeg(project))
            elif args.engine == "transcription":
                if not transcriber_ready(project):
                    install_python_package(project, TRANSCRIBER)
                if not transcriber_ready(project):
                    raise ValueError("Local transcription is unavailable. Check the Python wheel and native runtime.")
                print(local_python(project))
            else:
                if args.engine == "hyperframes":
                    prepare_ffmpeg(project)
                print(prepare_renderer(project, args.engine))
        elif args.command == "studio":
            return subprocess.call([sys.executable, str(SKILL / "studio.py"), *args.arguments], cwd=project,
                                   env=studio_environment(project))
        elif args.command == "transcribe":
            if not transcriber_ready(project):
                raise ValueError("Run prepare with transcription for this project first.")
            return subprocess.call([str(local_python(project)), str(SKILL / "speech.py"), *args.arguments],
                                   cwd=project)
        else:
            return run_engine(project, args.engine, args.arguments)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
