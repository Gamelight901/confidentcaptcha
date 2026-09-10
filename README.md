# Confident Captcha

> [!IMPORTANT]
> This is not an official project designed for public use. It's a school project, and should not be used outside of it's intended purpose as simply a project. Do not use for commerical/personal use, as it will be discontinued and delisted in the coming future.

A simple, self-hosted CAPTCHA. Instead of distorted text, the user is shown a set of semi-transparent, overlapping shapes and asked to click a specific one, e.g. **"Click the 'Orange Circle'"**. Every challenge is randomly generated (shapes, colors,positions, and depth order), and the server checks answers against a per-pixel "hit mask" of the actual rendered image, so the correct answer always matches what's visually on top.

## Accessiblity

> [!NOTE]
> This prototype does not cover accessibility options by design, sorry, however this is out of our control due to an implementation issue.

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

Debug mode is off by default; set `FLASK_DEBUG` to `=1` before running if you wantthe interactive debugger/auto-reload while developing.

Then open <http://127.0.0.1:5000> in a browser. Click the shape named in the prompt; a correct click shows a "Verification Successful" message with a link. An incorrect click will cause the program to generate a new prompt.

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
