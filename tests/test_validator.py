"""Tests for captcha.validator and captcha.store."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from captcha.generator import CaptchaChallenge, Shape
from captcha.renderer import render_challenge
from captcha.store import ChallengeStore, StoredChallenge
from captcha.validator import verify_click


def _single_circle_challenge():
	shape = Shape(id="only", kind="circle", color="green", x=100, y=100, size=80, z_index=0)
	# A lone shape wouldn't pass generate_challenge's overlap check, but the
	# renderer/validator only need a valid CaptchaChallenge shape, not a
	# generator-produced one.
	return CaptchaChallenge(id="test-challenge", shapes=(shape,), canvas_size=200)


def test_correct_click_passes():
	challenge = _single_circle_challenge()
	rendered = render_challenge(challenge)
	stored = StoredChallenge(correct_shape_id="only", rendered=rendered)
	result = verify_click(stored, 100, 100)
	assert result.success is True


def test_click_outside_shape_fails():
	challenge = _single_circle_challenge()
	rendered = render_challenge(challenge)
	stored = StoredChallenge(correct_shape_id="only", rendered=rendered)
	result = verify_click(stored, 5, 5)
	assert result.success is False


def test_click_on_wrong_shape_fails():
	shape_a = Shape(id="a", kind="circle", color="red", x=80, y=100, size=100, z_index=0)
	shape_b = Shape(id="b", kind="circle", color="blue", x=140, y=100, size=100, z_index=1)
	challenge = CaptchaChallenge(id="test-challenge", shapes=(shape_a, shape_b), canvas_size=200)
	rendered = render_challenge(challenge)
	stored = StoredChallenge(correct_shape_id="a", rendered=rendered)
	# (140, 100) is the center of "b", which is on top there.
	result = verify_click(stored, 140, 100)
	assert result.success is False


def test_store_is_single_use():
	store = ChallengeStore()
	challenge = _single_circle_challenge()
	rendered = render_challenge(challenge)
	stored = StoredChallenge(correct_shape_id="only", rendered=rendered)
	store.put("abc", stored)

	assert store.pop("abc") is stored
	assert store.pop("abc") is None


def test_store_returns_none_for_unknown_id():
	store = ChallengeStore()
	assert store.pop("missing") is None
