# Censor Agent Guide

The Censor Agent detects and bleeps profanity in videos by overlaying beep sounds at timestamps where offensive language is detected. It uses transcript analysis to identify profane words and produces a clean stream without modifying the original video.

## Prerequisites

1. **Video must exist in a collection**: The target video must be uploaded to VideoDB.
2. **Spoken words indexing**: The video must have spoken words indexed (the agent will index automatically if not already done).
3. **Beep audio**: A beep sound asset is required. The agent will:
   - Use the provided `beep_audio_id` if specified
   - Fall back to the `BEEP_AUDIO_ID` environment variable
   - Search the collection for an audio named "beep"
   - Upload a default beep sound if none found

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection_id` | `str` | Yes | Collection ID containing the video |
| `video_id` | `str` | Yes | Video ID to censor |
| `beep_audio_id` | `str` | No | Audio ID of the beep sound to use |
| `censor_prompt` | `str` | No | Custom instructions for what to censor |

## Implementation Steps

Follow these steps exactly to replicate the censor workflow:

### Step 1: Resolve Beep Audio

Resolve the beep audio in this priority order:

1. Use `beep_audio_id` parameter if provided
2. Fall back to `BEEP_AUDIO_ID` environment variable
3. Search the collection for an audio with "beep" in the name:
   ```python
   audios = videodb_tool.get_audios()
   for audio in audios:
       if "beep" in audio.get("name", "").lower():
           beep_audio_id = audio.get("id")
           beep_audio_length = audio.get("length")
           break
   ```
4. If none found, upload a default beep sound:
   ```python
   beep_audio = videodb_tool.upload(
       "https://www.youtube.com/watch?v=GvXbEO5Kbgc",
       media_type="audio",
       name="beep"
   )
   beep_audio_id = beep_audio.get("id")
   beep_audio_length = beep_audio.get("length")
   ```

**Alternative: Generate a beep sound**

If no beep audio exists, you can ask the user for permission to generate one using the sound effect generator:

```python
beep_audio = coll.generate_sound_effect(
    prompt="short censorship beep tone, 1 second, classic TV bleep sound",
    duration=1
)
beep_audio_id = beep_audio.id
```

### Step 2: Get Video Transcript with Timestamps

Retrieve the transcript with word-level timestamps (not plain text):

```python
try:
    transcript = videodb_tool.get_transcript(video_id, text=False)
except Exception:
    # Index spoken words if transcript not available
    videodb_tool.index_spoken_words(video_id)
    transcript = videodb_tool.get_transcript(video_id, text=False)
```

**Important**: Use `text=False` to get word-level timestamps required for precise beep placement.

### Step 3: Analyze Transcript for Profanity

Send the transcript to the LLM with the following prompt structure:

```
{censor_prompt}

OUTPUT FORMAT (STRICT):
Return a JSON object with "censored_items" array. Each item must have:
{
  "censored_items": [
    {
      "start": float,     // Exact start time in seconds (with decimals, e.g., 12.34)
      "end": float,       // Exact end time in seconds (with decimals, e.g., 12.89)
      "text": "word",     // The exact profane word/phrase being censored
      "severity": "high"  // Optional: "high", "medium", "low" - helps with filtering
    }
  ]
}

VALIDATION RULES (CRITICAL):
- start/end must be float values with decimal precision (e.g., 12.34, not 12)
- start must be STRICTLY LESS than end for each item
- **ABSOLUTELY NO OVERLAPPING RANGES**: For any two consecutive items, item[i].end must be less than item[i+1].start
- Leave at least 0.1 second gap between consecutive items to ensure no overlap
- If words are spoken back-to-back, use the exact transcript timestamps with tight boundaries
- If no profanity found, return {"censored_items": []}
- Return ONLY the JSON object, no markdown formatting (no ```json blocks)
- Sort items by start time (earliest first) and verify no overlaps exist

TRANSCRIPT TO ANALYZE:
{transcript}
```

Request JSON response format from the LLM:
```python
llm_response = llm.chat_completions(
    [message],
    response_format={"type": "json_object"}
)
```

### Step 4: Parse LLM Response

Clean and parse the JSON response (handle potential markdown formatting):

```python
response_content = llm_response.content.strip()
if response_content.startswith("```json"):
    response_content = response_content[7:]
if response_content.endswith("```"):
    response_content = response_content[:-3]
response_content = response_content.strip()

censor_response = json.loads(response_content)
censored_items = censor_response.get("censored_items", [])
timestamps = [(item["start"], item["end"]) for item in censored_items]
```

### Step 5: Merge Overlapping Timestamps

Merge overlapping timestamps to prevent audio overlay conflicts. Use 0.8 second buffer when checking overlaps (accounts for 0.4s padding added before and after):

```python
def merge_overlapping_timestamps(timestamps):
    if not timestamps:
        return []
    
    sorted_timestamps = sorted(timestamps, key=lambda x: x[0])
    merged = []
    
    for start, end in sorted_timestamps:
        if not merged:
            merged.append([start, end])
        else:
            last_start, last_end = merged[-1]
            # Check if current overlaps with previous (0.8s buffer)
            if start - 0.8 <= last_end:
                # Merge: extend the last range
                merged[-1][1] = max(last_end, end)
            else:
                merged.append([start, end])
    
    return [(s, e) for s, e in merged]

timestamps = merge_overlapping_timestamps(timestamps)
```

### Step 6: Create Timeline with Beep Overlays

Build the timeline with the video and beep audio overlays:

```python
from videodb.asset import VideoAsset, AudioAsset

beep_audio_length = float(beep_audio_length)
timeline = videodb_tool.get_and_set_timeline()

# Add video as inline asset
video_asset = VideoAsset(asset_id=video_id)
timeline.add_inline(video_asset)

# Add beep overlays at each censored timestamp
for start, end in timestamps:
    # Add 0.4 second buffer before and after the word
    buffered_start = start - 0.4
    buffered_end = end + 0.4
    
    # Trim beep length to fit duration (don't exceed beep audio length)
    length = min(beep_audio_length, (buffered_end - buffered_start))
    beep = AudioAsset(asset_id=beep_audio_id, end=length)
    
    # Place beep starting 0.4 seconds before the word
    adjusted_start = start - 0.4
    timeline.add_overlay(start=adjusted_start, asset=beep)
```

### Step 7: Generate Stream

Generate the final censored stream URL:

```python
stream_url = timeline.generate_stream()
```

### Step 8: Generate Censor Report Table

Create a markdown table summarizing censored items:

```python
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

table_rows = ["| # | Timestamp | Original Word | Action   |",
              "|---|-----------|---------------|----------|"]

for idx, item in enumerate(censored_items, 1):
    timestamp = format_timestamp(item["start"])
    word = item["text"]
    table_rows.append(f"| {idx} | {timestamp}  | {word}       | Censored |")

censor_table = "\n".join(table_rows)
```

## Complete Workflow Summary

For the reasoning engine to replicate the censor agent:

1. **Resolve beep audio** → Get `beep_audio_id` and `beep_audio_length`
2. **Get transcript** → `videodb_tool.get_transcript(video_id, text=False)` (index if needed)
3. **LLM analysis** → Send transcript with OUTPUT_PROMPT, request JSON response
4. **Parse response** → Extract `censored_items` array with start/end timestamps
5. **Merge overlaps** → Combine timestamps within 0.8s to prevent conflicts
6. **Build timeline** → Add video inline, add beep overlays with 0.4s buffer
7. **Generate stream** → `timeline.generate_stream()` returns clean stream URL
8. **Create report** → Generate markdown table of censored items

## Usage Examples

### Basic Censoring

```
User: "Censor the profanity in video m-abc123 from collection c-xyz789"
```

The agent will:
1. Find or create a beep sound
2. Get the video transcript with word-level timestamps
3. Send transcript to LLM for profanity detection
4. Parse JSON response and merge overlapping timestamps
5. Create timeline with beep overlays
6. Generate and return clean stream URL with censor table

### Custom Censor Instructions

```
User: "Censor all profanity and any mentions of competitor names in this video"
```

Custom `censor_prompt` can extend censoring beyond standard profanity to include brand names, sensitive topics, or context-specific terms. The custom prompt is prepended to the OUTPUT_PROMPT.

### Using Specific Beep Sound

```
User: "Censor video m-abc123 using the beep audio a-beep456"
```

Passing a specific `beep_audio_id` ensures consistent beep sounds across multiple censored videos.

## Output

The agent returns:

1. **Clean Stream URL**: A streamable video URL with beeps overlaid on profanity
2. **Censor Table**: A markdown table showing:
   - Index number
   - Timestamp (HH:MM:SS format)
   - Original word that was censored
   - Action taken (Censored)

Example censor table:
```
| # | Timestamp | Original Word | Action   |
|---|-----------|---------------|----------|
| 1 | 00:01:23  | word1         | Censored |
| 2 | 00:02:45  | word2         | Censored |
```

## Return Data

```python
{
    "stream_url": "https://stream.videodb.io/..."  # Clean censored stream
}
```

## Limitations

| Limitation | Detail |
|---|---|
| **Audio only** | The censor agent only censors spoken profanity in the audio track. It does not blur or censor visual content (text, gestures, etc.). |
| **Transcript dependent** | Accuracy depends on the quality of the spoken words transcript. Poor audio quality or heavy accents may affect detection. |
| **LLM interpretation** | Profanity detection relies on LLM judgment. Edge cases, slang, or context-dependent words may be missed or over-censored. |
| **No partial word censoring** | The entire word is beeped; cannot beep only part of a word. |
| **Fixed beep style** | The beep duration and buffering (0.4s before and after) are fixed. No customization of beep length or timing. |

## Integration with Timeline Editing

The censor agent uses the same timeline system described in [editor.md](editor.md). The censored stream can be further edited:

```python
# After censoring, the clean stream is just another video stream
# It can be used in additional timeline compositions
```

## Related

- [editor.md](editor.md) - Timeline editing and audio overlays
- [streaming.md](streaming.md) - Stream generation options
- [search.md](search.md) - Searching video content
