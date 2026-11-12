# Caption presets (render_timeline)

Offer two or three by name and recommend one. Never show colour codes. Unsure: Box Highlight.

Every preset sets `secondary_color`. Left unset it defaults to red, and the highlight animations (`box_highlight`, `color_highlight`, `karaoke`, `supersize`) paint the active word in it.

Sizes and margins are output pixels, tuned for a 1080-pixel short side (1920x1080 or 1080x1920). At 720, multiply `font.size`, `outline` and margins by 0.67.

Every asset below also carries `"type": "caption", "src": "auto"`.

| Preset | When | Caption asset fields |
|---|---|---|
| Box Highlight | Default | `font: {name: "Rubik", size: 50, bold: true}, animation: "box_highlight", primary_color: "&H00FFFFFF", secondary_color: "&H00FF00FF", back_color: "&H00000000", border: {style: "outline_and_shadow", outline: 2, outline_color: "&H00000000"}, position: {alignment: "bottom_center", margin_l: 15, margin_r: 15, margin_v: 40}` |
| TikTok Classic | Shorts, Reels, TikTok | `font: {name: "Montserrat", size: 58, bold: true}, animation: "impact", primary_color: "&H00FFFFFF", secondary_color: "&H0000FFFF", back_color: "&H80000000", border: {style: "outline_and_shadow", outline: 3, outline_color: "&H00000000"}, position: {alignment: "bottom_center", margin_l: 15, margin_r: 15, margin_v: 300}` |
| Karaoke | Word-by-word sing-along | `font: {name: "Open Sans", size: 56, bold: true}, animation: "karaoke", primary_color: "&H00FFFFFF", secondary_color: "&H0000FF00", back_color: "&H00000000", border: {style: "outline_and_shadow", outline: 3, outline_color: "&H00000000"}, position: {alignment: "bottom_center", margin_l: 30, margin_r: 30, margin_v: 30}` |
| Color Wave | Upbeat, product | `font: {name: "Noto Sans", size: 54, bold: true}, animation: "color_highlight", primary_color: "&H00FFFFFF", secondary_color: "&H005DE2F7", back_color: "&H00000000", border: {style: "outline_and_shadow", outline: 2, outline_color: "&H00000000"}, position: {alignment: "bottom_center", margin_l: 15, margin_r: 15, margin_v: 40}` |
| Bold Impact | Hype, sport, punchlines | `font: {name: "Oswald", size: 62, bold: true}, animation: "impact", primary_color: "&H00FFFFFF", secondary_color: "&H00FFFFFF", back_color: "&H00000000", border: {style: "outline_and_shadow", outline: 4, outline_color: "&H00000000"}, position: {alignment: "middle_center", margin_l: 15, margin_r: 15, margin_v: 20}` |
| Supersize Drama | Dramatic quotes | `font: {name: "Bebas Neue", size: 56, bold: false}, animation: "supersize", primary_color: "&H00FFFFFF", secondary_color: "&H0000FF00", back_color: "&H00000000", border: {style: "outline_and_shadow", outline: 3, outline_color: "&H00000000"}, position: {alignment: "middle_center", margin_l: 15, margin_r: 15, margin_v: 20}` |
| Cinematic Gold | Film, trailers | `font: {name: "Playfair Display", size: 52, italic: true}, animation: "reveal", primary_color: "&H0000D7FF", secondary_color: "&H0000FFFF", back_color: "&H00000000", border: {style: "outline_and_shadow", outline: 2, outline_color: "&H00000000"}, position: {alignment: "bottom_center", margin_l: 15, margin_r: 15, margin_v: 40}` |
| Modern Boxed | Corporate, explainers | `font: {name: "Libre Franklin", size: 44, bold: true}, animation: "reveal", primary_color: "&H00FFFFFF", secondary_color: "&H00FFFFFF", back_color: "&HE0000000", border: {style: "opaque_box", outline: 0, outline_color: "&H00000000"}, position: {alignment: "bottom_center", margin_l: 15, margin_r: 15, margin_v: 40}` |
| Clean Minimal | Calm, long form; no animation | `font: {name: "Lora", size: 46}, primary_color: "&H00FFFFFF", secondary_color: "&H00FFFFFF", back_color: "&HA0000000", border: {style: "outline_and_shadow", outline: 1, outline_color: "&H00000000"}, position: {alignment: "bottom_center", margin_l: 15, margin_r: 15, margin_v: 40}` (omit `animation`) |

On 9:16, keep bottom-anchored captions at `margin_v` 300 or more. The app's caption, username and music bar cover the bottom of the frame.

Colours are ASS `&HAABBGGRR`. A user who asks for a colour by name gets the matching code and never sees it. The `secondary_color` is the highlight: green `&H0000FF00`, yellow `&H0000FFFF`, magenta `&H00FF00FF`.

Say after the result: "I used the <preset> captions. Want <other preset> instead?"
