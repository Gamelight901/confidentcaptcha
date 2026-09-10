"""Flask application exposing the Confident Captcha demo.

Routes:
  GET  /              -- demo page
  GET  /api/challenge -- generate a new challenge (image + question)
  POST /api/verify    -- check a click against the stored challenge
"""
from base64 import b64encode

from flask import Flask, jsonify, render_template, request

from captcha.generator import generate_challenge
from captcha.question import build_question
from captcha.renderer import render_challenge
from captcha.store import ChallengeStore, StoredChallenge
from captcha.validator import verify_click

app = Flask(__name__)
store = ChallengeStore()


def _new_challenge_payload() -> dict:
	challenge = generate_challenge()
	rendered = render_challenge(challenge)
	question = build_question(challenge, rendered)
	store.put(
		challenge.id,
		StoredChallenge(correct_shape_id=question.shape_id, rendered=rendered),
	)
	image_data_url = "data:image/png;base64," + b64encode(rendered.png_bytes).decode("ascii")
	return {
		"challenge_id": challenge.id,
		"prompt": question.prompt,
		"image": image_data_url,
		"canvas_size": challenge.canvas_size,
	}


@app.get("/")
def index():
	return render_template("index.html")


@app.get("/api/challenge")
def api_challenge():
	return jsonify(_new_challenge_payload())


@app.post("/api/verify")
def api_verify():
	data = request.get_json(silent=True) or {}
	challenge_id = data.get("challenge_id")
	x = data.get("x")
	y = data.get("y")

	if not isinstance(challenge_id, str) or not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
		return jsonify({"error": "challenge_id, x and y are required"}), 400

	stored = store.pop(challenge_id)
	if stored is None:
		return jsonify({"success": False, "error": "challenge expired or already used", "next": _new_challenge_payload()})

	result = verify_click(stored, int(x), int(y))
	response: dict = {"success": result.success}
	if not result.success:
		response["next"] = _new_challenge_payload()
	return jsonify(response)


if __name__ == "__main__":
	app.run(debug=True)
