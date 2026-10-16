# Relay site

Pass the book. Keep the context.

This is the page the `/relay` skill opens: the inherited book ranked weakest first,
the ninety second brief as text, and the same brief voiced by a cloned voice on
ElevenLabs.

## How it updates

1. `/relay` scores a book and writes `dashboard.json` (via `relay/scripts/build_site.py`),
   `relay/brief.txt` and `relay/theme.txt`, then pushes to `main`.
2. The **Relay episode** GitHub Action fires on the brief change, voices it with
   ElevenLabs and commits `episodes/YYYY-MM-DD.mp3` + `episodes.json`.
3. Netlify redeploys on each push. `index.html` reads the two JSON files at load.

## Secrets (Settings → Secrets and variables → Actions)

- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`

Without them the action prints the script and stops cleanly; the page still shows
the dashboard and the brief as text.

## Sample books

`relay/assets/` holds two invented books. Every company, person and number is made up.
