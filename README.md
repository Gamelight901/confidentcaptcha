# Confident Captcha

A simple, self-hosted CAPTCHA demo built for a class project. Instead of
distorted text, the user is shown a set of semi-transparent, overlapping
shapes and asked to click a specific one, e.g. **"Click the 'Orange
Circle'"**. Every challenge is randomly generated (shapes, colors,
positions, and depth order), and the server checks answers against a
per-pixel "hit mask" of the actual rendered image, so the correct answer
always matches what's visually on top.

This is a school assignment demo, not a production security tool: it
intentionally uses a small, single Flask process with an in-memory,
single-use challenge store (no database, no session persistence, no
rate limiting). Restarting the server clears all outstanding challenges.

## Requirements

- Python 3.10+
- The packages listed in `requirements.txt` (Flask, Pillow, pytest)

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the demo

```bash
python3 app.py
```

Debug mode is off by default; set `FLASK_DEBUG=1` before running if you want
the interactive debugger/auto-reload while developing.

Then open <http://127.0.0.1:5000> in a browser. Click the shape named in
the prompt; a correct click shows a "Verification Successful" message
with a link (update the placeholder `href` in `templates/index.html`
with your own destination before presenting). An incorrect click loads
a brand-new challenge automatically.

Alternatively, using Flask's CLI:

```bash
flask --app app run
```

## Running the tests

```bash
python3 -m pytest
```

## Project layout

```
captcha/
  generator.py   # random shape/depth-order generation
  renderer.py     # Pillow-based drawing + per-pixel hit mask
  question.py     # picks a visible shape and builds the prompt text
  store.py         # in-memory, single-use challenge storage
  validator.py     # checks a click against the stored answer
app.py             # Flask routes (/, /api/challenge, /api/verify)
templates/         # HTML page
static/            # CSS + client-side JS
tests/             # pytest unit tests
```

## Known limitations (by design)

This prototype does not address accessibility concerns such as
colorblindness or screen-reader support, and only offers a single,
simple identification question style rather than more complex spatial
reasoning questions. These trade-offs are intentional scope decisions
for this assignment and are discussed further in the project report.
