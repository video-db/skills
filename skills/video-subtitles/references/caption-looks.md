# Caption looks

Offer two or three looks by name and recommend one. Never show colour codes. Unsure: Clean.

| Look | When | `add_subtitles` settings |
|---|---|---|
| Clean | Default; talks, demos, interviews | `font_size=26, bold=true, primary_colour="&H00FFFFFF", back_colour="&H80000000", border_style="opaque_box", alignment="bottom_center", margin_v=40` |
| Bold social | Shorts, Reels, TikTok | `font_size=34, bold=true, primary_colour="&H00FFFFFF", outline_colour="&H00000000", outline=3, border_style="outline", alignment="bottom_center", margin_v=220` |
| Yellow classic | Film, documentary | `font_size=26, primary_colour="&H0000FFFF", outline_colour="&H00000000", outline=2, border_style="outline", alignment="bottom_center"` |
| Podcast | Two people talking, long form | `font_size=24, primary_colour="&H00FFFFFF", back_colour="&H80000000", border_style="opaque_box", alignment="bottom_center", margin_v=30` |
| Tutorial | Screen recordings | `font_size=22, primary_colour="&H00FFFFFF", outline=2, border_style="outline", alignment="top_center"` (keeps the bottom of the screen clear) |
| Minimal | Clean edits, ads | `font_size=22, primary_colour="&H00FFFFFF", outline=1, shadow=1, border_style="outline", alignment="bottom_center"` |
| Karaoke | Word-by-word highlight | Not `add_subtitles`: `render_timeline` with a caption asset, `animation: "karaoke"` (the `video-edit` skill). The video must be transcribed first. |

Colours are ASS `&HAABBGGRR`: `&H00FFFFFF` opaque white, `&H80000000` half-transparent black, `&H0000FFFF` yellow. A user who asks for a colour by name gets the matching code; they never see the code.

Say after the result: "I used the <look> look. Want <other look> instead?"
