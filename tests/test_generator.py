"""Tests for captcha.generator."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from captcha.generator import COLORS, SHAPE_TYPES, generate_challenge


def test_generates_distinct_shapes_and_colors():
	challenge = generate_challenge(seed=1)
	kinds = [shape.kind for shape in challenge.shapes]
	colors = [shape.color for shape in challenge.shapes]
	assert len(kinds) == len(set(kinds))
	assert len(colors) == len(set(colors))
	assert set(kinds) <= set(SHAPE_TYPES)
	assert set(colors) <= set(COLORS)


def test_shape_count_within_bounds():
	challenge = generate_challenge(minimum_shapes=4, maximum_shapes=4, seed=2)
	assert len(challenge.shapes) == 4


def test_depth_order_is_a_permutation():
	challenge = generate_challenge(seed=3)
	z_indices = sorted(shape.z_index for shape in challenge.shapes)
	assert z_indices == list(range(len(challenge.shapes)))


def test_every_shape_overlaps_another():
	import math

	challenge = generate_challenge(seed=4)
	for shape in challenge.shapes:
		assert any(
			other.id != shape.id
			and math.hypot(shape.x - other.x, shape.y - other.y) < (shape.size + other.size) / 2
			for other in challenge.shapes
		)


def test_rejects_invalid_shape_bounds():
	with pytest.raises(ValueError):
		generate_challenge(minimum_shapes=1, maximum_shapes=1)
	with pytest.raises(ValueError):
		generate_challenge(minimum_shapes=5, maximum_shapes=3)


def test_rejects_small_canvas():
	with pytest.raises(ValueError):
		generate_challenge(canvas_size=50)


def test_challenge_ids_are_unique():
	challenge_a = generate_challenge(seed=5)
	challenge_b = generate_challenge(seed=6)
	assert challenge_a.id != challenge_b.id
