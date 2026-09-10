"""Question generation for the Confident Captcha challenge.

Picks a shape that is actually visible in the rendered image (i.e. not
fully hidden behind other shapes) and builds a simple identification
prompt such as ``Click the "Orange Circle"``.
"""
from dataclasses import dataclass
from typing import Final

from .generator import CaptchaChallenge
from .renderer import RenderedChallenge

# A shape must occupy at least this many visible pixels to be askable,
# so the user is never asked to find a shape that is almost entirely hidden.
MINIMUM_VISIBLE_PIXELS: Final[int] = 80


@dataclass(frozen=True, slots=True)
class Question:
	"""A question posed to the user and the shape id that answers it."""

	prompt: str
	shape_id: str


def _visible_pixel_counts(rendered: RenderedChallenge) -> dict[str, int]:
	counts: dict[str, int] = {}
	for row in rendered.hit_mask:
		for shape_id in row:
			if shape_id is not None:
				counts[shape_id] = counts.get(shape_id, 0) + 1
	return counts


def build_question(challenge: CaptchaChallenge, rendered: RenderedChallenge, *, rng=None) -> Question:
	"""Choose a clearly visible shape and build its identification prompt."""
	import random

	rng = rng or random.Random()
	visible_counts = _visible_pixel_counts(rendered)
	candidates = [
		shape
		for shape in challenge.shapes
		if visible_counts.get(shape.id, 0) >= MINIMUM_VISIBLE_PIXELS
	]
	if not candidates:
		# Fall back to any shape rather than failing outright; this should
		# only happen with pathological layouts.
		candidates = list(challenge.shapes)

	shape = rng.choice(candidates)
	return Question(prompt=f'Click the "{shape.label}"', shape_id=shape.id)
