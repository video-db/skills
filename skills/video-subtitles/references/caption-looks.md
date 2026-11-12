# Caption looks

Offer two or three looks by name and recommend one. Never show colour codes. Unsure: Clean.

| Look | When | `add_subtitles` settings |
|---|---|---|
| Clean | Default; talks, demos, interviews | `font_size=16, bold=true, primary_colour="&H00FFFFFF", back_colour="&H80000000", border_style="opaque_box", alignment="bottom_center", margin_v=12` |
| Bold social | Shorts, Reels, TikTok | `font_size=12, bold=true, primary_colour="&H00FFFFFF", outline_colour="&H00000000", outline=1.5, border_style="outline", alignment="bottom_center", margin_v=50` |
| Yellow classic | Film, documentary | `font_size=16, primary_colour="&H0000FFFF", outline_colour="&H00000000", outline=1, border_style="outline", alignment="bottom_center", margin_v=12` |
| Podcast | Two people talking, long form | `font_size=15, primary_colour="&H00FFFFFF", back_colour="&H80000000", border_style="opaque_box", alignment="bottom_center", margin_v=10` |
| Tutorial | Screen recordings | `font_size=14, primary_colour="&H00FFFFFF", outline=1, border_style="outline", alignment="top_center"` (keeps the bottom of the screen clear) |
| Minimal | Clean edits, ads | `font_size=14, primary_colour="&H00FFFFFF", outline=1, shadow=1, border_style="outline", alignment="bottom_center"` |
| Karaoke | Word-by-word highlight | Not `add_subtitles`: a `render_timeline` caption preset (the `video-edit` skill's `references/caption-presets.md`: Karaoke, Box Highlight, TikTok Classic and more). The video must be transcribed first. |

`margin_v` is the caption's distance from the bottom edge, not time padding. `font_size`, `outline` and the margins are not pixels of the video. They are measured on a 288-line canvas that is scaled to the frame height, so one value looks the same at 720p and 1080p: `margin_v=50` sits about 17% of the height above the bottom, and `font_size=16` is about 6% of the height. Bold social's 50 lifts captions above the app's caption and music bar on vertical video.

Colours are ASS `&HAABBGGRR`: `&H00FFFFFF` opaque white, `&H80000000` half-transparent black, `&H0000FFFF` yellow. A user who asks for a colour by name gets the matching code; they never see the code.

Say after the result: "I used the <look> look. Want <other look> instead?"
