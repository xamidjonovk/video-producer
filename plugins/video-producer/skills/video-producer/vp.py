"""Check local capabilities and prepare only the video engine selected for a job."""

import argparse
import json
import os
import platform
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
YT_DLP = "yt-dlp[default]==2026.11.23"
SCENEDETECT = "scenedetect[opencv-headless]==0.6.7.1"
EARSHOT = "earshot @ git+https://github.com/Leonxlnx/earshot@7a7f7c5c70d4a763a1eca4b3666af7c77e313f97"
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


def module_command(project, module):
    for executable in (local_python(project), Path(sys.executable)):
        if not executable.is_file():
            continue
        result = subprocess.run([str(executable), "-m", module, "--version"],
                                capture_output=True, check=False)
        if result.returncode == 0:
            return [str(executable), "-m", module]
    command = shutil.which(module.replace("_", "-"))
    return [command] if command else None


def prepare_module(project, module, package):
    command = module_command(project, module)
    if not command:
        install_python_package(project, package)
        command = module_command(project, module)
    if not command:
        raise ValueError(f"{module} was installed but could not start.")
    return command


def earshot_path(project):
    folder = local_python(project).parent
    executable = folder / ("earshot.exe" if os.name == "nt" else "earshot")
    return str(executable) if executable.is_file() else shutil.which("earshot")


def prepare_earshot(project):
    executable = earshot_path(project)
    if not executable:
        if not shutil.which("git"):
            raise ValueError("Earshot setup requires Git.")
        install_python_package(project, EARSHOT)
        executable = earshot_path(project)
    if not executable:
        raise ValueError("Earshot was installed but its CLI is unavailable.")
    subprocess.run([executable, "--help"], capture_output=True, check=True)
    return executable


def prepare_openscreen():
    commands = {
        "Windows": ("winget", "install", "--source", "msstore", "OpenScreen"),
        "Darwin": ("brew", "install", "--cask", "openscreen"),
    }
    command = commands.get(platform.system())
    if not command or not shutil.which(command[0]):
        raise ValueError("Use the official OpenScreen installer at https://github.com/getopenscreen/openscreen/releases.")
    subprocess.run([shutil.which(command[0]), *command[1:]], check=True)


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
    if not command:
        prepare_renderer(project, engine)
        command = engine_bin(directory, engine)
    if not node or not command:
        raise ValueError(f"{engine} requires a working Node.js 22+ runtime.")
    if engine == "hyperframes":
        prepare_ffmpeg(project)
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
        "yt_dlp_ready": module_command(project, "yt_dlp") is not None,
        "scenedetect_ready": module_command(project, "scenedetect") is not None,
        "earshot": earshot_path(project),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "plan", "prepare", "studio", "engine", "transcribe", "reference", "scenes", "sfx"):
        command = commands.add_parser(name)
        command.add_argument("project", type=Path)
        if name == "prepare":
            command.add_argument("engine", choices=("ffmpeg", "transcription", "yt-dlp", "scenedetect",
                                                   "earshot", "openscreen", *PACKAGES))
        if name == "reference":
            command.add_argument("url")
            command.add_argument("--limit", type=int, default=8)
            command.add_argument("--download-authorized", action="store_true")
        if name == "scenes":
            command.add_argument("source", type=Path)
            command.add_argument("output", type=Path)
        if name == "sfx":
            command.add_argument("description")
            command.add_argument("output", type=Path)
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
        elif args.command == "reference":
            from online_references import canonical_url, collect, video_url

            if args.download_authorized and not video_url(canonical_url(args.url)):
                raise ValueError("Use a single authorized video URL for media retrieval.")
            canonical_url(args.url)
            if not 1 <= args.limit <= 30:
                raise ValueError("Use a sample size from 1 to 30.")
            return collect(project, args.url, args.limit, prepare_module(project, "yt_dlp", YT_DLP),
                           args.download_authorized, ffmpeg(project) if args.download_authorized else None)
        elif args.command == "scenes":
            source = (project / args.source).resolve(strict=True)
            output = (project / args.output).resolve()
            if not source.is_file() or not output.is_relative_to(project):
                raise ValueError("Supply a media file and an output directory inside the project.")
            output.mkdir(parents=True, exist_ok=True)
            command = prepare_module(project, "scenedetect", SCENEDETECT)
            subprocess.run([*command, "--input", str(source), "--output", str(output),
                            "detect-content", "list-scenes"], cwd=project, check=True)
        elif args.command == "sfx":
            output = (project / args.output).resolve()
            if output.suffix.lower() != ".wav" or output.exists() or not output.is_relative_to(project):
                raise ValueError("Choose a new .wav output inside the project.")
            if args.description.startswith("-"):
                raise ValueError("Start the sound description with a word.")
            output.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([prepare_earshot(project), "make", args.description, "-o", str(output)],
                           cwd=project, check=True)
            if not output.is_file():
                raise ValueError("Earshot did not create the expected file.")
            print(output)
        elif args.command == "prepare":
            if args.engine == "ffmpeg":
                print(prepare_ffmpeg(project))
            elif args.engine == "yt-dlp":
                print(prepare_module(project, "yt_dlp", YT_DLP))
            elif args.engine == "scenedetect":
                print(prepare_module(project, "scenedetect", SCENEDETECT))
            elif args.engine == "earshot":
                print(prepare_earshot(project))
            elif args.engine == "openscreen":
                prepare_openscreen()
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
            if args.arguments and args.arguments[0] in ("inspect", "clean", "render", "draft"):
                if not any(argument in ("-h", "--help") for argument in args.arguments):
                    prepare_ffmpeg(project)
            return subprocess.call([sys.executable, str(SKILL / "studio.py"), *args.arguments], cwd=project,
                                   env=studio_environment(project))
        elif args.command == "transcribe":
            if not transcriber_ready(project):
                install_python_package(project, TRANSCRIBER)
            if not transcriber_ready(project):
                raise ValueError("Local transcription could not start in the project Python environment.")
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
