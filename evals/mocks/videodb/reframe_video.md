---
expect:
  video_id: string
  start: number
  end: number
  target: [vertical, square, landscape]
---
{"status": "processing", "output_url": "https://api.videodb.io/video/{{input.video_id}}/reframe/rf-test-0001", "poll_with": "get_job_result"}
