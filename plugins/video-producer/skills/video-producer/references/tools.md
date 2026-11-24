# Tool selection

Identify the production bottleneck before opening a provider or installing an engine. Treat each row as an available choice. Use the smallest set that can produce the brief and return the chosen engines and why they were needed.

| Need | Choose | First action |
| --- | --- | --- |
| Existing footage, multicam, HDR, clean speech cuts, color, sound | DaVinci Resolve or an existing capable NLE. Use local FFmpeg for inspection, pause-based rough cuts and delivery checks. | Inspect media. If Resolve scripting or MCP is available, work in a new timeline; otherwise supply a usable edit plan and SRT. |
| Titles, kinetic captions, HTML/CSS/GSAP motion, or overlays over footage | **HyperFrames** | Prepare the project-local engine, read its matching official skills when needed, and render a short test before compositing the full timeline. [Upstream](https://github.com/heygen-com/hyperframes) |
| React UI, data-driven explainer, design system, or many variants | **Remotion** | Reuse an existing Remotion project or prepare the bundled starter. Check usage eligibility, keep Remotion packages version-aligned, and render a test composition. [Upstream](https://github.com/remotion-dev/remotion), [license](https://www.remotion.dev/docs/license/pricing) |
| A launch film with custom musical scoring or an annotated visual revision workflow | **huashu-motion** | Prefer macOS, where upstream reports testing. Review the upstream skill and install it on demand using its documented `npx skills add alchaincyf/huashu-motion` route. Run its doctor. Download optional instrument samples only if the brief needs them, and record sample credits. Use HyperFrames plus authorized audio if dependencies are incompatible. [Upstream](https://github.com/alchaincyf/huashu-motion) |
| A sourced, chaptered technical explainer in English or Chinese using its prescribed design | **anything2explainer**, when its terms allow it | Check the PolyForm Noncommercial license and author authorization for commercial work. Follow the upstream install recipe in a separate project and verify TTS before rendering. For Uzbek or a paid client project without permission, use an original Remotion or HyperFrames layout, a sourced script, approved speech and timed captions. [Upstream](https://github.com/Vincentwei1021/anything2explainer) |
| A real UI action or a recorded screen demo is essential | **OpenScreen**, or existing OBS/native recorder | Reuse any installed recorder that meets the brief. If OpenScreen is needed, use its Windows Store distribution or official macOS/Linux release. Record only the project window and use an existing export or official AI controls when present. [Upstream](https://github.com/getopenscreen/openscreen) |
| A shot must appear to share one continuous camera move across several beats | **onetake**, when its terms allow it | Use the upstream skill only for noncommercial work or with a suitable license. For other client work, design an original continuous camera setup in HyperFrames or Remotion. QA transitions at full playback speed, including continuity and motion blur. [Upstream](https://github.com/feitangyuan/onetake) |
| Reference examples of authored animation style | **Lemo Opuscar** | Study only relevant styles. Load the external skill only if its style library is actually needed. Check file-level licenses and the upstream film-production permission before carrying over material. Use original graphics and no library redistribution. [Upstream](https://github.com/lemomo-ai/lemo-opuscar) |
| Precise layers, masks, keyframes, alpha exports, or compositor projects | **EffectCraft** or existing Resolve Fusion | Inspect the existing editor and choose based on the editable deliverable. Install EffectCraft from its official release when needed. Prefer `effectcraft-cli` for supported engine actions; use its documented MCP bridge only for a task that needs GUI-only commands. Test project save and alpha before relying on it. [Upstream](https://github.com/storytold/effectcraft) |
| Photoreal moving insert or narrative shot that real footage cannot provide | Higgsfield or another connected video provider | Estimate the candidate model and test the hardest shot. Prefer an existing clip, original recording, local graphics or properly licensed stock when it fills the same story beat. [Credit workflow](higgsfield.md) |
| Natural speech, timing, or original sound | User recording, local transcription, ElevenLabs or another authorized provider | Keep performances that work. Test pronunciation and duration before batch TTS. Preserve stems and prefer SRT timed to the edited audio. |
| Research or publishing prep | Selected public sources, vidIQ, FFmpeg delivery package | Research without uploading source media. Obtain user authorization for exact asset, destination and caption before sending or publishing content. [Trend workflow](trends.md) |

## Run local engines

Resolve the skill path once and then use absolute paths where your shell needs them:

```text
python <skill>/vp.py doctor <project>
python <skill>/vp.py prepare <project> ffmpeg
python <skill>/vp.py prepare <hyperframes-project> hyperframes
python <skill>/vp.py engine <hyperframes-project> hyperframes doctor
python <skill>/vp.py engine <hyperframes-project> hyperframes render
python <skill>/vp.py prepare <job> remotion
python <skill>/vp.py engine <job> remotion render src/index.tsx Title title.mp4
```

Use the HyperFrames source project as its working directory. Read the pinned CLI's help before passing project flags. Remotion runs inside the editable `remotion/` folder of the specified job. Copy or retain that folder with the deliverable. On Windows or macOS, desktop app installs, Chrome downloads, and screen capture permissions can involve OS or account prompts. Surface the specific prompt if it blocks the selected production step.
