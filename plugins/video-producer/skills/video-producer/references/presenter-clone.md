# Presenter cloning from original footage

Use this workflow to make a real presenter deliver new words in existing footage. Use the person's own recording or video and voice material they have explicitly authorized for this use. A creator's public post can inform style and pacing. The picture and voice used in the clone must come from authorized source files.

## What the tutorial demonstrated

| Time | Mabrur Dev's experiment |
| --- | --- |
| 0:41–1:19 | Demo Reel. The edit uses existing footage, new narration and a script informed by five of the creator's previous Reels. |
| 2:55–4:09 | He gathered his Reels as style references and tried making the presenter move from still photos. He found the result too synthetic. |
| 4:09–6:05 | He used his verified ElevenLabs Professional Voice Clone and auditioned two speech renders with different settings before committing to the video. |
| 7:08–9:34 | He compared a Magnific lip-sync attempt and a still animated in Seedance 2.5 and then passed through lip sync. He rejected both presenter results. In the Seedance pass the gestures and head movements were invented before the new speech was applied. |
| 9:34–10:47 | He switched to a real existing clip and used Higgsfield Sync Lipsync 3 with the new voice track. The on-screen project report shows the presenter pass split into five parts cut around pauses and edited into a 46.8-second Reel. |
| 10:47–12:49 | He recommends a clear vertical talking-head take with natural movement, a separate voice track, lip sync, and a final motion edit informed by references. He notes the cost of treating this as a high-volume workflow. |

[Mabrur Dev’s YouTube tutorial](https://www.youtube.com/watch?v=LISXexyRnxo).

## Prepare a real performance and lock the voice

1. Read the brief and match the delivery to the footage. For a recurring series, extract the opening style, sentence length and visual pacing from a few authorized Reels. Use the notes to draft the new script and cut plan.
2. Pick a continuous, sharply focused take of one presenter. Keep the eyes, mouth and chin visible. Prefer even light, an eye-level camera and a clear view of the teeth during speech. For a new reference recording use the intended delivery aspect, a steady camera, unobstructed mouth and natural gestures. Choose the performance whose emphasis and movement best match the new lines.
3. Lock a clean speech track before any paid video pass. Use the real recording when provided. When the task calls for a voice clone, reuse a suitable verified ElevenLabs voice. If the presenter needs to create a Professional Voice Clone, use ElevenLabs' owner-verification flow and its current recording guidance. Listen to an Uzbek sample for stress, names, numbers and breathing. Compare a second short voice sample when the first leaves a meaningful performance decision open.
4. Align each audio phrase with a usable video range, accounting for natural pauses. Cut around pauses and existing shot boundaries. Keep format and timing stable. The tutorial's on-screen notes discuss 25 fps as a cost consideration. Check the exact quote and choose another frame rate only when it suits the shoot and delivery.

```text
python <skill>/vp.py lipsync-prep <project> <original-video> <final-speech> <job>/assets/presenter-01 --video-start 12 --audio-start 3 --seconds 8
```

The command produces a silent `presenter.mp4`, mono `speech.wav` and `inputs.json` for one take. It preserves the source files and runs locally. Choose a new folder for each pair. Check the resulting duration, framing, visible face and the speech around the endpoints before quoting. HDR follows the local Rec.709 conversion path. For Dolby Vision or tricky log footage, export a color-managed source first.

## Apply Sync Lipsync 3

Use the prepared **original video** as the video input and the prepared **speech** as the audio input. Keep the original acting, framing and gestures as the baseline. For this route, skip Seedance and still-to-video animation.

- On Higgsfield, check the current connector catalog for the exact Sync Labs model and its true video and audio roles. Search results may contain nearby models. If the exact model and both roles are supported, quote the prepared pair, use the shared credit ledger and submit the exact quote after authorization. Retrieve the returned job and import its finished media.
- If the connector omits that model, open Higgsfield **Video → Lipsync Studio → Sync Lipsync 3** in the authorized browser, use its supported upload controls for both files, and verify the displayed price before generation. If this surface cannot run the task and the user already has authorized direct Sync access, use **sync-3** via official sync. labs Studio or API. Direct access uses its own billing and credentials. A missing provider or scope can leave a ready local pair and a precise handoff.
- Price one 6–10 second take or one complete compatible line first. Mark the quoted surface and duration. Save the receipt and result before continuing. If a result is late, check its job status before spending again.

## Edit and verify

Play the first take at normal speed with the target audio. Watch lip closure on **m**, **b**, **p**, then the stressed vowels, teeth, jaw edges, blink and head turn. Compare gestures and identity to the source, and check the last word and silence at each splice. Focus on the first failing timecode before replacing any material. Keep coverage changes local to the weak passage. Use original footage, licensed B-roll and restrained motion graphics to support the script. Retain the clean speech track on the timeline and use the processed take's matching timebase so a duplicate dialogue track cannot play. Deliver the MP4, timed captions and editable timeline or plan. Record the final visual check separately from the file and audio measurements.

[Higgsfield Lipsync Studio help](https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-lipsync-voiceover-and-aspect-ratios) · [Sync Labs model](https://sync.so/docs/models/sync-3) · [Sync Labs media tips](https://sync.so/docs/compatibility-and-tips/media-content-tips) · [ElevenLabs Professional Voice Cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning).
