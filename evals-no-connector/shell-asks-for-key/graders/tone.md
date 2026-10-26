---
type: llm
---

PASS if the reply asks the user for their VideoDB API key in a friendly way (free at console.videodb.io, no card), says it will set things up once the key is given (or offers /mcp as an alternative), and does not claim to have found the moment or made a clip.
FAIL if it tells the user to set environment variables themselves as the only option, pastes a long setup tutorial, asks several questions at once, or invents a result.
