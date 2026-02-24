# Meeting Recording Guide

VideoDB can process meeting recordings to extract transcripts, generate structured summaries, identify action items and decisions, and produce searchable, clippable archives of any meeting.

## Prerequisites

A meeting recording must be uploaded as a video (or audio) to a collection before analysis. The recording must be **indexed for spoken words** to enable transcript extraction, search, and LLM-based analysis.

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()

# Upload meeting recording
meeting = coll.upload(url="https://example.com/standup-2024-01-15.mp4")

# Index spoken words (required for all meeting operations)
meeting.index_spoken_words(force=True)
```

## Transcript Extraction

### Full Transcript

```python
# Timestamped transcript entries
transcript = meeting.get_transcript()
for entry in transcript:
    print(f"[{entry['start']:.1f}s - {entry['end']:.1f}s] {entry['text']}")
```

### Plain Text

```python
# Full text without timestamps (useful for LLM input)
text = meeting.get_transcript_text()
print(text)
```

## AI-Powered Meeting Analysis

Use `coll.generate_text()` to run LLM analysis on meeting content. This is a method on the **Collection** object that accepts a prompt and a model tier. Pass the transcript text directly in the prompt.

### Generate Summary

```python
text = meeting.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this meeting transcript:\n{text}\n\n"
        "Summarize this meeting. Include:\n"
        "1. A 2-3 sentence executive summary\n"
        "2. Key topics discussed\n"
        "3. Important points raised by participants\n"
        "Keep the summary concise and professional."
    ),
    model_name="pro",
)
print(result["output"])
```

### Extract Action Items

```python
text = meeting.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this meeting transcript:\n{text}\n\n"
        "Extract all action items from this meeting. "
        "For each action item, provide:\n"
        "- Description of the task\n"
        "- Who is responsible (if mentioned)\n"
        "- Deadline or timeframe (if mentioned)\n"
        "Format as a numbered list."
    ),
    model_name="pro",
)
print(result["output"])
```

### Extract Decisions

```python
text = meeting.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this meeting transcript:\n{text}\n\n"
        "Identify all decisions made during this meeting. "
        "For each decision, provide:\n"
        "- What was decided\n"
        "- Context or reasoning (if discussed)\n"
        "- Who made or approved the decision (if clear)\n"
        "Format as a numbered list."
    ),
    model_name="pro",
)
print(result["output"])
```

### Full Structured Analysis

Combine everything into a single structured output:

```python
text = meeting.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this meeting transcript:\n{text}\n\n"
        "Analyze this meeting and provide a structured report:\n\n"
        "## Summary\n"
        "Provide a concise executive summary (2-3 sentences).\n\n"
        "## Key Topics\n"
        "List the main topics discussed.\n\n"
        "## Action Items\n"
        "List each action item with owner and deadline if mentioned.\n\n"
        "## Decisions\n"
        "List each decision made with context.\n\n"
        "## Follow-ups\n"
        "List any items that need follow-up or further discussion."
    ),
    model_name="pro",
)
print(result["output"])
```

### Using Different Model Tiers

```python
text = meeting.get_transcript_text()

# Basic tier (fastest, lower cost)
result = coll.generate_text(
    prompt=f"Given this transcript:\n{text}\n\nSummarize this meeting.",
    model_name="basic",
)

# Pro tier (balanced)
result = coll.generate_text(
    prompt=f"Given this transcript:\n{text}\n\nSummarize this meeting.",
    model_name="pro",
)

# Ultra tier (highest quality)
result = coll.generate_text(
    prompt=f"Given this transcript:\n{text}\n\nSummarize this meeting.",
    model_name="ultra",
)
```

## Searching Meeting Content

After indexing, search within the meeting for specific topics:

```python
from videodb import SearchType

# Find where "budget" was discussed
results = meeting.search("budget discussion", search_type=SearchType.semantic)

for shot in results.get_shots():
    print(f"[{shot.start:.1f}s - {shot.end:.1f}s] {shot.text}")
```

### Extract a Clip for a Specific Topic

```python
results = meeting.search("quarterly targets", search_type=SearchType.semantic)
shots = results.get_shots()

if shots:
    # Stream just the matching segment
    stream_url = shots[0].generate_stream()
    print(f"Clip: {stream_url}")
```

### Compile All Mentions of a Topic

```python
from videodb.timeline import Timeline
from videodb.asset import VideoAsset

results = meeting.search("action items", search_type=SearchType.semantic)
shots = results.get_shots()

timeline = Timeline(conn)
for shot in shots:
    asset = VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
    timeline.add_inline(asset)

stream_url = timeline.generate_stream()
print(f"All action-item segments: {stream_url}")
```

## Visual Analysis with Scene Indexing

For meetings with screen shares, presentations, or whiteboard content, index scenes to enable visual search:

```python
from videodb import SceneExtractionType, SearchType, IndexType

# Index visual scenes
meeting.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 15, "select_frames": ["first", "last"]},
    prompt="Describe the visual content: slides, screen shares, diagrams, or whiteboard notes.",
)

# Search by visual content
results = meeting.search(
    "presentation slide with chart",
    search_type=SearchType.semantic,
    index_type=IndexType.scene,
)
```

### Combined Visual + Transcript Analysis

```python
from videodb import SceneExtractionType

# Index scenes for visual content
meeting.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 15, "select_frames": ["first", "last"]},
    prompt="Describe any slides, screen shares, or visual content shown.",
)

# Get transcript and use collection LLM for combined analysis
text = meeting.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this meeting transcript:\n{text}\n\n"
        "Analyze this meeting using the spoken content. "
        "List each topic discussed and the key points made about it."
    ),
    model_name="pro",
)
print(result["output"])
```

## Recording a Live Meeting

Use `record_meeting()` to send a bot into a live meeting and record it directly:

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()

# Start recording a live meeting
meeting = coll.record_meeting(
    meeting_url="https://meet.google.com/abc-defg-hij",
    bot_name="RecorderBot",
)

# Wait for the meeting to finish
meeting.wait_for_status("done")

# Refresh to get the video_id
meeting.refresh()

# Access the recorded video
video = coll.get_video(meeting.video_id)
video.index_spoken_words(force=True)

# Now analyze as usual
text = video.get_transcript_text()
result = coll.generate_text(
    prompt=f"Given this meeting transcript:\n{text}\n\nSummarize this meeting.",
    model_name="pro",
)
print(result["output"])
```

## Cross-Meeting Search

Search across all meeting recordings in a collection:

```python
coll = conn.get_collection()

results = coll.search(
    query="quarterly revenue",
    search_type=SearchType.semantic,
)

for shot in results.get_shots():
    print(f"Video: {shot.video_id} [{shot.start:.1f}s - {shot.end:.1f}s] {shot.text[:80]}")
```

## Complete Workflow Examples

### Weekly Standup Processing

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()

# Upload and index
standup = coll.upload(url="https://example.com/standup-recording.mp4")
standup.index_spoken_words(force=True)

# Get transcript
transcript_text = standup.get_transcript_text()
print(f"Transcript length: {len(transcript_text)} chars")

# Full analysis
result = coll.generate_text(
    prompt=(
        f"Given this daily standup transcript:\n{transcript_text}\n\n"
        "Provide:\n"
        "1. Summary of what each person reported\n"
        "2. Blockers mentioned\n"
        "3. Action items with owners\n"
        "Keep it concise — bullet points preferred."
    ),
    model_name="pro",
)
print(result["output"])
```

### Meeting Minutes with Auto-Subtitles

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()

meeting = coll.get_video("meeting-video-id")

# Generate subtitles for the recording
meeting.index_spoken_words(force=True)
subtitle_url = meeting.add_subtitle()
print(f"Meeting with subtitles: {subtitle_url}")

# Stream the original video
stream_url = meeting.play()
print(f"Meeting playback: {stream_url}")

# Generate minutes
text = meeting.get_transcript_text()
result = coll.generate_text(
    prompt=(
        f"Given this meeting transcript:\n{text}\n\n"
        "Generate formal meeting minutes. Include:\n"
        "- Date and participants (if identifiable)\n"
        "- Agenda items discussed\n"
        "- Decisions made\n"
        "- Action items with assignees\n"
        "- Next meeting topics"
    ),
    model_name="pro",
)
print(result["output"])
```

### Build a Searchable Meeting Archive

```python
import videodb
from videodb import SearchType

conn = videodb.connect()
archive = conn.create_collection(name="Meeting Archive", description="All team meetings")

# Batch upload meeting recordings
urls = [
    "https://example.com/meeting-jan-15.mp4",
    "https://example.com/meeting-jan-22.mp4",
    "https://example.com/meeting-jan-29.mp4",
]

for url in urls:
    video = archive.upload(url=url)
    video.index_spoken_words(force=True)
    print(f"Indexed: {video.name} ({video.id})")

# Now search across all meetings
results = archive.search(
    query="hiring plan for Q2",
    search_type=SearchType.semantic,
)

for shot in results.get_shots():
    print(f"{shot.video_id}: [{shot.start:.1f}s - {shot.end:.1f}s] {shot.text[:100]}")
```

## Tips

- **Index once**: `index_spoken_words()` is a one-time operation per video. Subsequent searches and transcript calls are fast.
- **Prompt quality matters**: Specific, structured prompts produce better meeting analysis. Include the expected output format in the prompt.
- **Choose the right model tier**: `basic`, `pro`, and `ultra` offer different trade-offs between speed and quality. Use `pro` for most meeting analysis.
- **Pass transcript in the prompt**: `coll.generate_text()` is a collection-level method. Fetch the transcript with `get_transcript_text()` and include it in the prompt string.
- **Trim long meetings**: For very long recordings, search for specific segments first, then analyse those segments individually for more focused results.
- **Scene indexing for slides**: If the meeting includes screen shares or presentations, `index_scenes()` enables searching by visual content.
- **Combine with timelines**: Use search results with `Timeline` to create compilations of specific discussion topics across multiple meetings (see [editor.md](editor.md)).
- **Record live meetings**: Use `coll.record_meeting()` to send a bot into a Google Meet, Zoom, or other meeting URL and record directly into VideoDB.
