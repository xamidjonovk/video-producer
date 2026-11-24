# Video Producer

One agent for local video editing, screen demos, code-driven motion and budgeted AI footage. Install the workflow once and let it choose the tools for each project. The core supports local video references, pause-based rough cuts, subtitle-ready editing, audio mixing, FFmpeg technical checks and publication drafts.

## Install from a repo link

Give a terminal-enabled assistant the repository link and this instruction:

> Install Video Producer from this repository for my current editor. Read the README and manifests, add the marketplace or use the project installer if the marketplace is unavailable, then check which capabilities work. Set up renderers only when a project needs them.

Use [xamidjonovk/video-producer](https://github.com/xamidjonovk/video-producer) as the repository URL.

| App | Marketplace installation | Invoke after installation |
| --- | --- | --- |
| **ChatGPT Desktop in Codex** | Open **Plugins**, choose **Add plugin marketplace**, paste the repository URL and install **Video Producer**. With the CLI, run `codex plugin marketplace add xamidjonovk/video-producer`, then `codex plugin add video-producer@video-producer`. | Start a new task and describe the video |
| **Claude Desktop with Plugins** | Open **Settings → Plugins → Add → Add Marketplace → Add from a repository**, paste the repository URL, sync, then install **Video Producer**. | Describe the video in an environment with project files and terminal access |
| **Claude Code** | Run `/plugin marketplace add xamidjonovk/video-producer`, then `/plugin install video-producer@video-producer`. | Start a new session and describe the video |

Marketplace access can depend on the app and workspace configuration. Local renderers require an environment with access to the video files and to a terminal for the host's installed binaries. A chat-only surface can produce scripts and shot plans. [Codex marketplace example](https://github.com/openai/community-plugins), [Claude Desktop marketplace example](https://developers.openai.com/learn/developers-codex-plugin).

### Local installation

Use this from a checkout if you need a local copy of the skill without the marketplace. Python 3.10 or later is required for the helper scripts. Use your system's `python3` or `py -3` launcher if `python` is unavailable.

```sh
python install.py codex
python install.py claude
# Or install into a single project:
python install.py both --project "/path/to/video-project"
```

The user install writes to `~/.agents/skills/video-producer` for Codex and `~/.claude/skills/video-producer` for Claude Code. It can be run again on the same version. If an older or customized copy is present, the installer reports its path so it can be backed up before replacement. [Codex local skills](https://learn.chatgpt.com/docs/build-skills), [Claude skills](https://code.claude.com/docs/en/skills).

## Use it

After installation, describe the job in a regular message. The host can automatically select the skill based on the request and the skill chooses the production tools. A direct skill invocation is also available for sessions where host settings limit automatic selection.

> Bu iPhone videomdan 40 soniyalik o‘zbekcha Reel tayyorla. Tabiiy ovozni saqla. Shu Instagram va YouTube linklarini pacing referensi sifatida ishlat. Subtitr va tahrirlanadigan montaj rejasini ber.

> Turn this release brief into a 25-second demo. Record the real interface, add motion only where it clarifies the feature, and deliver the MP4 and editable source.

> Create a cinematic teaser. My Higgsfield limit is 180 credits. Test the most difficult shot before generating the rest.

### Local commands

From the checkout, this is the skill directory:

```text
plugins/video-producer/skills/video-producer
```

```text
python <skill>/vp.py doctor <project>
python <skill>/vp.py plan <project> raw-edit
python <skill>/vp.py prepare <project> ffmpeg
python <skill>/references_tool.py add <project> <video-or-link>
python <skill>/vp.py studio <project> init jobs/reel-01 --mode iphone
python <skill>/vp.py studio <project> clean jobs/reel-01 "/path/to/take.mp4"
python <skill>/vp.py studio <project> render jobs/reel-01 --plan clean-edit.json
```

The FFmpeg setup reuses the current binary, or installs a pinned FFmpeg wheel into an isolated environment inside the project. Supply `VIDEO_AGENT_FFMPEG` and `VIDEO_AGENT_FFPROBE` to use existing binaries that are off PATH. HTML and React renderers require Node.js 22+ and prepare separately. Local transcription uses the project's Python environment and downloads the selected model on first use. The agent can apply the official install recipes for optional desktop tools when a specific task calls for them. [Tool selection and setup](plugins/video-producer/skills/video-producer/references/tools.md), [specialist tools](plugins/video-producer/skills/video-producer/references/specialists.md).

## External accounts and media

Higgsfield, ElevenLabs, vidIQ and other account-based connectors use the host's official connection flow. Paid generations use the project budget and a live quote. Add personal research handles in your own project's `watchlist.local.json` with the structure of the bundled [watchlist](plugins/video-producer/skills/video-producer/watchlist.json).

The Video Producer code and templates use the [MIT license](LICENSE). Third-party software, providers, sample assets and styles follow their respective terms. The [tool selection guide](plugins/video-producer/skills/video-producer/references/tools.md) links to the upstream terms and handles commercial-use cases.
