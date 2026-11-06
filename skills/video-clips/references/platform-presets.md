# Platform presets

If the user names a platform, use its row and do not ask. If the format changes the output and they didn't say, ask once (a choice card where the host has one): "Shorts / Reels / TikTok (vertical)", "Square for the feed", "Landscape for YouTube".

| They say | `reframe_video` target | Captions |
|---|---|---|
| Shorts, Reels, TikTok, Stories, "vertical" | `"vertical"` (9:16, 1080x1920), `mode="smart"` | Bold social |
| Instagram or LinkedIn feed, "square" | `"square"` (1:1, 1080x1080) | Clean |
| Portrait feed post | `{"width": 1080, "height": 1350}` (4:5) | Clean |
| YouTube, "landscape", a website | `"landscape"` (16:9, 1920x1080) | Clean |

A platform sets the shape and the captions, not the length. Use the length the user gave. If they gave none, choose it from the material: Shorts and Reels take up to about 3 minutes and TikTok longer; most work best under a minute, and an informative clip can justify more. Say the length you chose before starting and invite a change. Always pass `start` and `end`; whole videos are slow. If smart mode fails, use simple mode and say the subject may not stay centred.
