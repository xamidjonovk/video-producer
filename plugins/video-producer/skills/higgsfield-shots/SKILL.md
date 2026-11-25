---
name: higgsfield-shots
description: Direct, quote, review or repair individual AI-generated shots when Higgsfield is selected or a cinematic brief needs generated motion, consistent characters, product fidelity or synchronized dialogue. Activate for that part of a production. Local cuts, captions, color and ordinary reference research stay with the editor.
---

# Higgsfield Shots

Follow the active host's connector schema. For a named preset use the provider's preset route and confirm it honors the user's chosen model before submission. A research or price request ends at the findings or quote.

For final generated footage, explicitly set Higgsfield MAGI-2 (`magi_2`) unless the user requests another video model. Follow the [cinematic workflow](../video-producer/references/cinematic.md) for reusable references, MAGI-2 input modes and continuity. If the selected route cannot use the chosen model, flag the affected shot and continue with the available planning or editing work until the user chooses how to proceed.

For lip sync on an authorized existing presenter video, use the [presenter cloning workflow](../video-producer/references/presenter-clone.md). It uses the original moving footage and audio as the two inputs to Sync Lipsync 3.

## Before the first paid take

- Lay out the edit with the actual dialogue and existing footage. Mark only the gaps that need generated movement. Choose a representative beat that tests the hardest requirement and can be used in the final cut. Match final aspect, motion and resolution whenever they matter to acceptance.
- Keep one small shot card in the job. Record its ID, usable duration and handles, frame size, opening pose, visible action and ending pose. Attach confirmed reference IDs with explicit roles. Reuse the same character, wardrobe, prop and location references across shots. Describe who handles each object, their screen position, eyeline and light direction. Attach only the references this shot uses.
- Frame for the story. A medium shot shows a handoff, a reaction close-up shows the eyes, and a wide shot establishes geography. Give the actor one playable action and choose a camera move or a locked frame. Put optical and lighting controls in the supported settings. Use the prompt for what changes over time.
- Example direction for a five-second vertical office shot: “Medium close-up. The manager sets the blue folder on the desk with her right hand, waits for the click of the latch, then looks left toward the door.” Keep the prop reference and side light from the previous shot. Record Foley separately when the mix needs control.
- For dialogue, audition the real line first, especially Uzbek names, stress and vowels. Use an authorized native recording as a reference when the chosen model and shot mode accept it. Test a short native-dialogue take when needed. Check the first mouth closure, a stressed syllable and the last word at normal speed with sound. Preserve an accepted performance. Dubbing, inserting a reaction, or using an off-camera line must still serve the brief.

## Spend and resume

Find the current model, supported inputs, format and duration. Fetch a live quote for one take by default. For a batch, use its quoted **request total**. Compare direct final versus a supported draft plus final only if the draft tests the actual uncertainty. A draft that passes is useful when it can be finalized from its returned ID. Count both charges. Price media edits on their actual billable input duration. Keep free web entitlements and connector quotes distinct.

Use the job's local ledger for paid submissions. Replace the angle-bracketed fields below. An existing authorized cap suffices. Quote-only work needs no ledger.

```text
python <this-skill>/takes.py <job> init --cap <authorized-cap>
python <this-skill>/takes.py <job> status
python <this-skill>/takes.py <job> hold <shot-id> <quote-ref> <quoted-total>
python <this-skill>/takes.py <job> link <quote-ref> <provider-job-id> [more-job-ids]
python <this-skill>/takes.py <job> finish <quote-ref> kept <confirmed-charge> "<chosen job ID and QA note>"
```

Initialize once per budget scope. For an existing production include previous confirmed charges with `--spent` and any protected allowance with `--reserve`. Use one shared ledger for shots covered by the same cap. Submit the exact quoted request only after a successful new hold in this run. Reopening a job, a timeout, or a lost response means reconciling the hold with provider history and job IDs before doing anything paid. Keep the hold while billing is unknown. Record a confirmed failed submission or unused reservation with `finish ... failed` and its actual charge. Use `rejected` for a completed, charged take that failed review. A new attempt for that shot needs a fresh quote and `hold ... --retry`. Use `status` to find and reuse an accepted take. The ledger uses whole-credit ceilings for planning. See the [multi-shot budget calculator](../video-producer/references/higgsfield.md) for comparing plans.

If earlier work predates the ledger and its charge is unknown, reconcile it against provider history before allocating that money. Continue local editing in the meantime. If the provider later confirms a refund on a closed take, run `takes.py <job> refund <quote-ref> <remaining-net-charge> <billing-receipt>`. This restores the confirmed difference and retains its receipt.

## Review and repair

Play at delivery size with sound. Check face, product markings, hands and contacts, physical action, sharpness, dialogue, screen direction and the cut against the adjacent shot. Log the first failing timecode. A still or transcript only verifies what it shows. Check picture and voice again after any edit.

| Observed issue | First intervention |
| --- | --- |
| Good performance, incorrect grade, audio level, title or trim | Keep the video. Adjust only the relevant layer in the editor. |
| Brief object drift or a shot ending early | Compare a targeted edit or extension quote with a retake. Preserve the approved frames and check the seam. |
| Identity swaps, broken physics or unnatural mouth movement throughout | Fix the reference role, action or voice input. Change the identified cause and test the affected shot. |
| Approved detail is lost at final size | Inspect the original and final. Use a better reference or a final-resolution take if necessary. Upscale only once the underlying shot passes. |

Higgsfield's worked material covers [product references](https://higgsfield.ai/academy/courses/ai-creation/product-images-and-ads), [assets](https://higgsfield.ai/academy/courses/ai-creation/create-and-edit-assets), [framing](https://higgsfield.ai/academy/courses/ai-creation/shot-sizes-and-prompting), [two-person scenes](https://higgsfield.ai/blog/two-characters-one-scene-ai-video), [camera and lighting](https://higgsfield.ai/blog/how-to-make-ai-video-look-filmed), [lip sync](https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-lipsync-voiceover-and-aspect-ratios) and [targeted edits](https://higgsfield.ai/blog/how-to-edit-videos-with-ai).
