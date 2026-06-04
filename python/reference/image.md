# Image Object Reference

```python
image = coll.get_image(image_id)
```

## Image Properties

| Property | Type | Description |
|----------|------|-------------|
| `image.id` | `str` | Unique image ID |
| `image.collection_id` | `str` | Parent collection ID |
| `image.name` | `str` | Image name |
| `image.url` | `str\|None` | Image URL (may be `None` for generated images — use `generate_url()` instead) |

## Image Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `image.generate_url()` | `str` | Generate signed URL |
| `image.delete()` | `None` | Delete the image |

## Generating Images

Image objects can be created from a `Collection` via AI generation. See [generative.md](generative.md) for full details.

```python
image = coll.generate_image(
    prompt="a sunset over mountains",
    aspect_ratio="16:9",   # "1:1", "9:16", "16:9", "4:3", or "3:4"
)
```

## Thumbnails

Thumbnails are `Image` objects produced from a video.

```python
# Generate one thumbnail at a specific timestamp (returns an Image)
thumb = video.generate_thumbnail(time=5.0)

# Generate a URL for the default thumbnail (no Image created)
thumb_url = video.generate_thumbnail()

# Fetch all thumbnails on a video
thumbs = video.get_thumbnails()
```

## Using Images in Timelines

Image objects are added to a timeline as an overlay via `ImageAsset`. See [editor.md](editor.md) for the full Editor API.

```python
from videodb.asset import ImageAsset

asset = ImageAsset(
    asset_id=image.id,
    duration=None,        # display duration (seconds)
    width=100,            # display width
    height=100,           # display height
    x=80,                 # horizontal position (px from left)
    y=20,                 # vertical position (px from top)
)
timeline.add_overlay(start=0, asset=asset)
```
