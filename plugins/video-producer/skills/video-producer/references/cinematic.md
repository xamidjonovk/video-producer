# Direct AI video and short films

Apply the screenplay, asset sheets and shot direction from the [Santiago breakdown](https://higgsfield.ai/blog/Santiago-breakdown). Keep the user's story, cast and delivery format. Use the selected motion model's own inputs and timing limits.

## 1. Write the script and lock the references

Break `script.json` into scenes with a dramatic beat, intended duration, speaking character, exact dialogue and a visible action. Mark what the audience learns in each beat. Write for the target aspect ratio and leave time for reactions and pauses. Decide the visual rules once per sequence, including light direction, color palette, contrast, camera movement and tone.

Run `vp.py studio <project> init <job> --mode cinematic` for a new film or `--mode broll` for a generated insert job. Use the same command with the existing job path when adding generation to an edit. Keep the approved files and versions.

| Job folder | Contents | Source for new references |
| --- | --- | --- |
| `Character/` | A sheet per recurring role or meaningful outfit or age variant. Use full-body front and back plus a face close-up, at consistent scale on neutral gray with even light. | [Soul Cinema](https://higgsfield.ai/generate?imageModel=soul_cinematic), model `soul_cinematic`. Anchor variants to the approved character image. |
| `Location/` | Clean establishing plates that show room geography, fixed landmarks, practical lights and time of day. Use a three-quarter view to establish depth. Make an alternate angle only when the coverage needs it. | Soul Cinema (`soul_cinematic`). Reuse the established plate as a reference for an alternate angle. |
| `Props/` | Clean, evenly lit product sheets. Record scale, materials, colors and authorized markings. Add matching front and back views when both are seen. | Built-in OpenAI ImageGen for new product-style props. Follow the host's `imagegen` instructions and copy the selected output into the job. Use supplied product photography as the fidelity reference where available. |
| `generation/` | Shot cards, prompts, transition frames and generated takes. Use stable IDs such as `S02_K03_take-01.mp4`. | [Higgsfield MAGI-2](https://higgsfield.ai/magi-2-intro) (`magi_2`) for final video. An explicit request can select a different video model. |

Reuse approved references first. Record each asset's stable alias, path, version, role and confirmed provider media ID when available in `assets.md`. Use the same aliases on each shot card. Attach the actual files or confirmed media IDs supported by the selected model. Alias text alone does not attach a reference. Build only the references that need to stay recognizable across shots or that carry story or product detail.

## 2. Direct the shots

For each shot in `generation/`, record its ID and edit duration, opening pose, timed action, final pose, approved asset aliases, speaker and exact dialogue. Describe framing, angle, focus, movement, screen position, eyeline, light direction, ambience and Foley. Assign a clear action or reaction to each beat and use timestamps where timing matters. Give movement a visible cause and props believable weight and contact.

Choose a wide shot for geography, a medium shot for a physical exchange and a close-up for a reaction. Keep the camera on one side of the 180-degree line for matched eyelines, and carry positions, hands, wardrobe and prop state across the cut. Use a Dutch angle, match cut or whip pan when it serves the story. For a match cut, reuse the previous accepted end frame when the next shot can use it as a start frame. For a whip pan, name the starting subject, duration and framing at the landing. Describe the expected image and behavior in concrete terms.

Write dialogue verbatim in the requested language. For Uzbek, keep natural phrasing, names and pronunciation. State who speaks, when they start, where the pause falls and what the other actor does. Keep room tone and Foley under the words. Review accent, mouth movement and the entire line at normal speed before committing the remaining shots.

## 3. Quote, generate and assemble

- Pass the model ID explicitly to the active connector. Use `magi_2` for the final shot unless the user selected another model. If the selected model or the intended input mode is unavailable, flag the affected shot and keep the script, edit and references usable. Obtain the user's choice before switching models.
- Verify MAGI-2's current catalog schema before quoting. The currently documented Higgsfield connector offers 1080p, whole-second requests from 4 to 30 seconds and optional native audio. Choose only the needed duration with usable edit handles. A short editorial beat can be trimmed from a supported take.
- MAGI-2 reference mode accepts image, video and audio references. Use it for recurring identities, places, products or a clean voice reference where supported. MAGI-2 frame mode accepts a start frame and an optional end frame. It is separate from reference mode. If a match cut needs both an exact starting composition and other references, use a composed start frame with the essential details already present, or create the join in the editor. Verify supported media fields for the active surface.
- Price assets and shots before paid submission. Present the plan, model, request totals and expected credit spend within the user's budget. Follow [Higgsfield Shots](../../higgsfield-shots/SKILL.md) for live quotes, approval scope, holds and receipts. Start with one representative take that can be kept in the final edit, ideally the hardest continuity, action or dialogue beat. Check that take before quoting or submitting dependent shots.
- Assemble accepted takes in the editable timeline. Watch neighboring cuts with sound at delivery size. Check identity, location geography, prop markings, screen direction, action matching, focus, Uzbek pronunciation where applicable and visible lip sync. Repair the affected shot or edit layer and retain the accepted takes. Finish mix, captions and export in the editor.
