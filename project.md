# Project Progress

## Overview
This project is a NUST admissions chatbot built with FastAPI, FAISS, and sentence-transformer embeddings. The chatbot answers questions from `app/faq.json`, uses `app/faiss_index/faq.index` for semantic search, and serves a web UI from `app/templates/index.html` and `app/static/style.css`.

## Work Completed

### FAQ and Index Updates
- Confirmed the FAQ training flow is handled by `app/embed.py`.
- Verified that the updated `app/faq.json` had expanded from the original smaller set to 306 entries.
- Rebuilt the FAISS index so the new questions were included.
- Later appended 11 additional basic conversational questions such as:
  - `How are you?`
  - `Who are you?`
  - `What is your name?`
  - `Can you help me?`
  - `What can I ask you?`
  - `What do you do?`
  - `Are you a human?`
  - `Can you guide me?`
  - `How do I use this chatbot?`
  - `Can you answer general questions?`
  - `Good morning`
- Rebuilt the index again after those additions.
- Final verified FAQ/index count: 317 entries.

### UI / Frontend Changes
Updated the chatbot UI in `app/templates/index.html` and `app/static/style.css`.

Implemented:
- Light and dark mode toggle with saved preference.
- Distinct textured backgrounds for light and dark mode.
- Additional ambient/fluid motion effects.
- NUST logo integration using `logo.png`, copied to `app/static/logo.png`.
- Send button changed from text to a right-arrow icon.
- Heading changed from `NUST FAQ Assistant` to `NUST Admission Assistant`.
- Wider page layout.
- Visible chat scrolling and improved scroll behavior.
- Sticky/static header behavior.

### Related Questions Improvements
- Improved semantic search behavior so related questions appear more often.
- Updated backend logic so:
  - best answers still require a stronger threshold,
  - related questions can come from weaker but still relevant matches,
  - low-confidence queries can still show related suggestions instead of forcing a bad direct answer.
- Updated API flow in `app/main.py` to support that distinction.

### Related Questions UI Behavior
There were two iterations:
1. Related questions were temporarily changed into clickable suggestion buttons that submitted a new query.
2. This was reverted at user request.

Current final behavior:
- Related questions remain inline inside the same answer card.
- Clicking a related question expands/collapses its answer like a dropdown.
- It does not send a new query.

## Key Files Changed
- `app/faq.json`
- `app/faiss_index/faq.index`
- `app/templates/index.html`
- `app/static/style.css`
- `app/static/logo.png`
- `app/search.py`
- `app/main.py`

## Current Search Behavior
- `app/search.py` now separates:
  - `best_match`
  - `related`
- `app/main.py` returns:
  - direct answer + related questions when a strong match exists
  - fallback message + related questions when no strong direct match exists

## Notes About `.claude`
- The repo contains a `.claude` folder with `settings.local.json`.
- It appears to store Claude-specific local permissions/config.
- Renaming `.claude` would likely stop Claude tooling from using those settings.
- It should not affect the chatbot app itself, but it is not a zero-impact change for tooling.
- The folder was not renamed.

## Final State
At this point the project includes:
- updated FAQs and retrained index,
- improved UI styling and theme support,
- sticky header,
- NUST branding/logo,
- more consistent related-question suggestions,
- inline dropdown related answers,
- preserved backend app flow.
