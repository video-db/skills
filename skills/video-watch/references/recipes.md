# Footage recipes

Tested paths for understanding footage in chat. Follow the steps.

## A shot list from footage

For: "what's in this footage", "sort my B-roll", "find all the wide outdoor shots".

1. Get the videos (links in chat; for a folder of local files, use Claude Code and the SDK).
2. Run `understand_video` on each with cheap settings and fixed lists:
   ```
   understand_video(video_id,
     segmentation={"type": "shot", "threshold": 30},
     sampling={"strategy": "uniform", "frame_count": 2},
     transform={"resolution": "480p"},
     analyzers=[{"type": "vlm", "name": "footage", "config": {"model": "basic",
       "prompt": "Describe the shot.",
       "schema": {"shot_size": {"type": "string", "enum": ["close-up", "medium", "wide"]},
                  "location": {"type": "string", "enum": ["indoor", "outdoor"]},
                  "people": {"type": "string", "enum": ["none", "one", "group"]},
                  "usable": {"type": "string", "enum": ["yes", "no"]},
                  "description": "string"}}}])
   ```
   Use the same analyzer name for every video so you can search across them.
3. `create_index` for that analyzer on each video.
4. Answer with search plus a filter ("car on an open road" where shot_size is "wide"). Labels can drift ("wide shot", "wide_shot"), so exact counts are unreliable: use search with a filter, and say counts are approximate.
5. Deliver a table: video name, time, shot size, location, description, link. Next steps: "Make a rough-cut reel of the usable wide shots", "Find every close-up across my footage".

## Break down an ad

For: "deconstruct this ad", "what makes this video work", "make a style guide from these ads".

1. `generate_transcript`, then `understand_video` with the same cheap settings (3 frames per shot) and a vlm schema: shot type, camera motion, subject, on-screen text, layout, palette, energy.
2. Deliver a shot table with times, the average shot length, the opening, where the product first appears, the palette and the on-screen text. For several ads, write one style guide with a shot table per ad.
3. Say once: "VideoDB can't hear music or sound effects yet, so this covers picture, text and speech." Never guess sounds from the pictures.
4. Next steps: "Find every pack shot with a slogan across these ads", "Cut my footage in this style".
