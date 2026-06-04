# Video Object Reference

```python
video = coll.get_video(video_id)
```

## Video Properties

| Property | Type | Description |
|----------|------|-------------|
| `video.id` | `str` | Unique video ID |
| `video.collection_id` | `str` | Parent collection ID |
| `video.name` | `str` | Video name |
| `video.description` | `str` | Video description |
| `video.length` | `float` | Duration in seconds |
| `video.stream_url` | `str` | Default stream URL |
| `video.player_url` | `str` | Player embed URL |
| `video.thumbnail_url` | `str` | Thumbnail URL |

## Video Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `video.generate_stream(timeline=None)` | `str` | Generate stream URL (optional timeline of `[(start, end)]` tuples) |
| `video.play()` | `str` | Open stream in browser, returns player URL |
| `video.search(query, search_type, index_type, result_threshold, score_threshold, dynamic_score_percentage, filter, **kwargs)` | `SearchResult` | Search within video. Pass `scene_index_id` via `**kwargs` to target a specific scene index. |
| `video.add_subtitle(style=SubtitleStyle())` | `str` | Add subtitles (returns stream URL) |
| `video.generate_thumbnail(time=None)` | `str\|Image` | Generate thumbnail — returns URL if `time` omitted, otherwise an `Image` object |
| `video.get_thumbnails()` | `list[Image]` | Get all thumbnails |
| `video.get_transcript(start=None, end=None, segmenter=Segmenter.word, length=1, force=None)` | `list[dict]` | Get timestamped transcript segments |
| `video.get_transcript_text(start=None, end=None)` | `str` | Get full transcript text |
| `video.generate_transcript(force=None)` | `dict` | Generate transcript |
| `video.translate_transcript(language, additional_notes="", callback_url=None)` | `list[dict]` | Translate transcript to another language |
| **Spoken-word indexing** | | |
| `video.index_spoken_words(language_code=None, segmentation_type=SegmentationType.sentence, force=False, callback_url=None)` | `None` | Index speech for search. Use `force=True` to skip if already indexed (idempotent). There is **no list method for spoken-word indexes** — `force=True` is the correct way to make the call safe to re-run. |
| **Scene indexing** | | |
| `video.index_scenes(extraction_type, extraction_config, prompt, metadata, model_name, model_config, name, scenes, callback_url)` | `str` | Index visual scenes (returns `scene_index_id`). Raises `InvalidRequestError` if an index already exists — either call `list_scene_index()` first, or catch the error and extract the existing id from the message. |
| `video.index_visuals(prompt, batch_config, model_name, model_config, name, callback_url)` | `str` | Index visuals via `batch_config` (returns `scene_index_id`). `batch_config` keys: `type` (`"time"`, `"shot"`), `value`, `frame_count`, `select_frames`. |
| `video.index_audio(prompt, model_name, model_config, language_code, batch_config, name, callback_url)` | `str` | Index audio by running transcript segments through an LLM (returns `scene_index_id`). `batch_config` keys: `type` (`"word"`, `"sentence"`, `"time"`), `value`. |
| `video.list_scene_index()` | `list` | **List all scene indexes** on this video. Call this before `index_scenes()` to check whether an index already exists. |
| `video.get_scene_index(scene_index_id)` | `list` | Get the records stored in a specific scene index |
| `video.delete_scene_index(scene_index_id)` | `None` | Delete a scene index |
| **Scene extraction (boundaries without LLM descriptions)** | | |
| `video.extract_scenes(extraction_type=SceneExtractionType.shot_based, extraction_config={}, force=False, callback_url=None)` | `SceneCollection\|None` | Extract scene boundaries without running LLM description. Raises if scenes already extracted for this video — use `force=True` to rebuild, or call `list_scene_collection()` first. |
| `video.list_scene_collection()` | `list` | List all scene collections (from prior `extract_scenes` calls) |
| `video.get_scene_collection(collection_id)` | `SceneCollection\|None` | Get a specific scene collection by id |
| `video.delete_scene_collection(collection_id)` | `None` | Delete a scene collection |
| **Editing & reframing** | | |
| `video.reframe(start=None, end=None, target="vertical", mode=ReframeMode.smart, callback_url=None)` | `Video\|None` | Reframe video aspect ratio. Returns `None` when `callback_url` is provided (async). |
| `video.smart_vertical_reframe(start=None, end=None, callback_url=None)` | `Video\|None` | Convenience shortcut for `reframe(target="vertical", mode="smart")` |
| `video.clip(prompt, content_type, model_name)` | `SearchResult` | Generate a clip from a prompt. `content_type` ∈ `"spoken"`, `"visual"`, `"multimodal"`; `model_name` ∈ `"basic"`, `"pro"`, `"ultra"`. |
| `video.insert_video(video, timestamp)` | `str` | Insert another video at `timestamp`. Returns the stream URL of the composite. |
| **Meeting & storage** | | |
| `video.get_meeting()` | `Meeting\|None` | Get the `Meeting` object associated with this video (for videos produced by `record_meeting`), or `None` |
| `video.download(name=None)` | `dict` | Download the video via its stream URL. Raises `ValueError` if `stream_url` is not set. |
| `video.remove_storage()` | `None` | Remove the video's storage while keeping the metadata record |
| `video.delete()` | `None` | Delete the video completely |

## Reframe

Convert a video to a different aspect ratio with optional smart object tracking. Processing is server-side.

> **Warning:** Reframe is a slow server-side operation. It can take several minutes for long videos and may time out. Always use `start`/`end` to limit the segment, or pass `callback_url` for async processing.

```python
from videodb import ReframeMode

# Always prefer short segments to avoid timeouts:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1080, "height": 1080})
```

### reframe Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | `float\|None` | `None` | Start time in seconds (None = beginning) |
| `end` | `float\|None` | `None` | End time in seconds (None = end of video) |
| `target` | `str\|dict` | `"vertical"` | Preset string (`"vertical"`, `"square"`, `"landscape"`) or `{"width": int, "height": int}` |
| `mode` | `str` | `ReframeMode.smart` | `"simple"` (centre crop) or `"smart"` (object tracking) |
| `callback_url` | `str\|None` | `None` | Webhook URL for async notification |

Returns a `Video` object when no `callback_url` is provided, `None` otherwise.

## Video Search Parameters

```python
results = video.search(
    query="your query",
    search_type=SearchType.semantic,       # semantic, keyword, or scene
    index_type=IndexType.spoken_word,      # spoken_word or scene
    result_threshold=None,                 # max number of results
    score_threshold=None,                  # minimum relevance score
    dynamic_score_percentage=None,         # percentage of dynamic score
    scene_index_id=None,                   # target a specific scene index (pass via **kwargs)
    filter=[],                             # metadata filters for scene search
)
```

> **Note:** `filter` is an explicit named parameter in `video.search()`. `scene_index_id` is passed through `**kwargs` to the API.

> **Important:** `video.search()` raises `InvalidRequestError` with message `"No results found"` when there are no matches. Always wrap search calls in try/except. For scene search, use `score_threshold=0.3` or higher to filter low-relevance noise.

For scene search, use `search_type=SearchType.semantic` with `index_type=IndexType.scene`. Pass `scene_index_id` when targeting a specific scene index. See [search.md](search.md) for details.

## SearchResult Object

```python
results = video.search("query", search_type=SearchType.semantic)
```

| Method | Returns | Description |
|--------|---------|-------------|
| `results.get_shots()` | `list[Shot]` | Get list of matching segments |
| `results.compile()` | `str` | Compile all shots into a stream URL |
| `results.play()` | `str` | Open compiled stream in browser |

### Shot Properties

| Property | Type | Description |
|----------|------|-------------|
| `shot.video_id` | `str` | Source video ID |
| `shot.video_length` | `float` | Source video duration |
| `shot.video_title` | `str` | Source video title |
| `shot.start` | `float` | Start time (seconds) |
| `shot.end` | `float` | End time (seconds) |
| `shot.text` | `str` | Matched text content |
| `shot.search_score` | `float` | Search relevance score |

| Method | Returns | Description |
|--------|---------|-------------|
| `shot.generate_stream()` | `str` | Stream this specific shot |
| `shot.play()` | `str` | Open shot stream in browser |
