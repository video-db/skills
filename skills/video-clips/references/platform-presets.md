# Platform presets

If the user names a platform, use its row and do not ask. If the format changes the output and they didn't say, ask once (a choice card where the host has one): "Shorts / Reels / TikTok (vertical)", "Square for the feed", "Landscape for YouTube".

| They say | `reframe_video` target | Length default | Captions |
|---|---|---|---|
| Shorts, Reels, TikTok, Stories, "vertical" | `"vertical"` (9:16, 1080x1920), `mode="smart"` | 30 to 45 s, never over 60 unless asked | Bold social |
| Instagram or LinkedIn feed, "square" | `"square"` (1:1, 1080x1080) | 30 to 60 s | Clean |
| Portrait feed post | `{"width": 1080, "height": 1350}` (4:5) | 30 to 60 s | Clean |
| YouTube, "landscape", a website | `"landscape"` (16:9, 1920x1080) | As asked | Clean |

Always pass `start` and `end`; whole videos are slow. If smart mode fails, use simple mode and say the subject may not stay centred.
