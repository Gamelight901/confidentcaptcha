"""Tests for captcha.renderer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from captcha.generator import CaptchaChallenge, Shape
from captcha.renderer import render_challenge, shape_id_at


def _two_overlapping_circles():
	# Bottom circle centered at (100, 100), top circle centered at (140, 100);
	# both radius 60 (size 120), so they overlap around x in [80, 160].
	bottom = Shape(id="bottom", kind="circle", color="red", x=100, y=100, size=120, z_index=0)
	top = Shape(id="top", kind="circle", color="blue", x=140, y=100, size=120, z_index=1)
	return CaptchaChallenge(id="test-challenge", shapes=(bottom, top), canvas_size=240)


def test_topmost_shape_wins_in_overlap_region():
	challenge = _two_overlapping_circles()
	rendered = render_challenge(challenge)
	# (140, 100) is the center of the top circle -- clearly in overlap territory
	# and also covered by the bottom circle's bounding area.
	assert shape_id_at(rendered, 140, 100) == "top"


def test_non_overlapping_region_reports_correct_shape():
	challenge = _two_overlapping_circles()
	rendered = render_challenge(challenge)
	# (60, 100) is only within the bottom circle (x in [40, 160]) but far enough
	# from the top circle's center (140, 100) that only "bottom" covers it.
	assert shape_id_at(rendered, 45, 100) == "bottom"


def test_background_pixel_has_no_shape():
	challenge = _two_overlapping_circles()
	rendered = render_challenge(challenge)
	assert shape_id_at(rendered, 5, 5) is None


def test_out_of_bounds_pixel_returns_none():
	challenge = _two_overlapping_circles()
	rendered = render_challenge(challenge)
	assert shape_id_at(rendered, -1, -1) is None
	assert shape_id_at(rendered, 10_000, 10_000) is None


def test_png_bytes_are_produced():
	challenge = _two_overlapping_circles()
	rendered = render_challenge(challenge)
	assert rendered.png_bytes.startswith(b"\x89PNG")
