# Platform presets

If the user names a platform, use its row and do not ask. If the format changes the output and they didn't say, ask once (a choice card where the host has one): "Shorts / Reels / TikTok (vertical)", "Square for the feed", "Landscape for YouTube".

| They say | `reframe_video` target | Captions |
|---|---|---|
| Shorts, Reels, TikTok, Stories, "vertical" | `"vertical"` (9:16; keeps the source height, so a 720p source gives 404x720), `mode="smart"` | Bold social |
| Instagram or LinkedIn feed, "square" | `"square"` (1:1) | Clean |
| Portrait feed post | `{"width": 1080, "height": 1350}` (4:5) | Clean |
| YouTube, "landscape", a website | `"landscape"` (16:9, 1920x1080) | Clean |

A named platform turns captions on in its look unless the user says no captions. Pass these to `add_subtitles` on the reframed video (same values as the `video-subtitles` skill's caption looks):

| Look | `add_subtitles` settings |
|---|---|
| Bold social | `font_size=12, bold=true, primary_colour="&H00FFFFFF", outline_colour="&H00000000", outline=1.5, border_style="outline", alignment="bottom_center", margin_v=50` |
| Clean | `font_size=16, bold=true, primary_colour="&H00FFFFFF", back_colour="&H80000000", border_style="opaque_box", alignment="bottom_center", margin_v=12` |

`margin_v` is the distance from the bottom edge. `font_size`, `outline` and the margins are not pixels of the video. They are measured on a 288-line canvas that is scaled to the frame height, so one value looks the same at 720p and 1080p: `margin_v=50` sits about 17% of the height above the bottom, and `font_size=16` is about 6% of the height. Bold social's 50 lifts captions above the app's caption and music bar on vertical video.

A platform sets the shape and the captions, not the length. Use the length the user gave. If they gave none, choose it from the material: Shorts and Reels take up to about 3 minutes and TikTok longer; most work best under a minute, and an informative clip can justify more. Say the length you chose before starting and invite a change. Always pass `start` and `end`; whole videos are slow. If smart mode fails, use simple mode and say the subject may not stay centred.
