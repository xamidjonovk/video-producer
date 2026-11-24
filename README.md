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

### References and finishing

Give the agent an Instagram profile, YouTube channel, or individual video link as part of a normal brief. It samples public metadata, records access status and uses local footage or an authorized connector for visual and audio analysis. The relevant commands prepare yt-dlp, PySceneDetect, and Earshot on first use if needed.

```text
python <skill>/vp.py reference <project> "https://www.youtube.com/@OpenAI/shorts" --limit 8
python <skill>/vp.py scenes <project> <source> <job>/inspection
python <skill>/vp.py sfx <project> "a soft paper rustle" <job>/assets/paper.wav
```

New edit plans support Rec.709 SDR delivery, tagged HDR tone mapping, clip-level grade controls, timed sound layers, music ducking, and measured AAC loudness and true peak. The technical report records the measured output. Use playback to check the picture and mix. [Online references](plugins/video-producer/skills/video-producer/references/online.md), [finishing guide](plugins/video-producer/skills/video-producer/references/finishing.md), [publishing workflow](plugins/video-producer/skills/video-producer/references/publish.md).

## External accounts and media

### Spend less on revisions

Version 0.4.0 bundles **Higgsfield Shots** for projects that need generated footage. Both marketplace hosts and the local installer include it alongside Video Producer. A brief can mix an existing performance with a single generated insert. Keep the original dialogue, approve the hardest shot first, and fix trim, captions, color or sound on the accepted take in the editor. [Shot direction and credit receipts](plugins/video-producer/skills/higgsfield-shots/SKILL.md).

The agent requests a live quote and records a hold before submitting each paid take. Pending holds consume the shared job budget, including after a lost response. Completed takes carry provider IDs and a review note. To inspect a job, run `python plugins/video-producer/skills/higgsfield-shots/takes.py <job> status`. A quote by itself spends zero credits.

For reference-heavy briefs the agent uses `vp.py reference <project> <url> --brief`. This prints the fields needed to shortlist clips and keeps the fuller report in the project. Revision handoffs carry the affected shot IDs, decisions and file locations. Final exports use one complete audio/video decode for corruption checks, sampled luma and optional measured loudness/true peak. A measured constant gain preserves natural dynamics when the mix has enough headroom for AAC encoding.

Higgsfield, ElevenLabs, vidIQ and other account-based connectors use the host's official connection flow. Paid generations use the project budget and a live quote. Add personal research handles in your own project's `watchlist.local.json` with the structure of the bundled [watchlist](plugins/video-producer/skills/video-producer/watchlist.json).

The Video Producer code and templates use the [MIT license](LICENSE). Third-party software, providers, sample assets and styles follow their respective terms. The [tool selection guide](plugins/video-producer/skills/video-producer/references/tools.md) links to the upstream terms and handles commercial-use cases.
