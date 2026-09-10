"""Core data generation for the Confident Captcha challenge.

The renderer, question builder, and web API all build on the records
produced here without needing to know how a challenge was randomized.
"""
from dataclasses import dataclass
from itertools import combinations
from secrets import token_urlsafe
from typing import Final
from uuid import uuid4
import math
import random


SHAPE_TYPES: Final[tuple[str, ...]] = (
	"circle",
	"square",
	"star",
	"triangle",
	"hexagon",
	"diamond",
	"pentagon",
)
COLORS: Final[tuple[str, ...]] = (
	"red",
	"yellow",
	"blue",
	"green",
	"purple",
	"orange",
	"cyan",
)


@dataclass(frozen=True, slots=True)
class Shape:
	"""One visible object in a generated depth stack."""

	id: str
	kind: str
	color: str
	x: int
	y: int
	size: int
	z_index: int

	@property
	def label(self) -> str:
		"""Human readable name used in the challenge question, e.g. "Orange Circle"."""
		return f"{self.color.capitalize()} {self.kind.capitalize()}"


@dataclass(frozen=True, slots=True)
class CaptchaChallenge:
	"""Server-side challenge data used to render and validate a CAPTCHA."""

	id: str
	shapes: tuple[Shape, ...]
	canvas_size: int


def _shapes_overlap(a: Shape, b: Shape) -> bool:
	"""Approximate overlap test using each shape's bounding circle."""
	distance = math.hypot(a.x - b.x, a.y - b.y)
	return distance < (a.size + b.size) / 2


def _has_meaningful_overlap(shapes: tuple[Shape, ...]) -> bool:
	"""Require every shape to overlap at least one other shape.

	This keeps the transparency/depth-order effect visible for every
	shape instead of allowing isolated, non-overlapping shapes.
	"""
	if len(shapes) < 2:
		return False
	overlapping_ids = {
		shape.id
		for shape_a, shape_b in combinations(shapes, 2)
		if _shapes_overlap(shape_a, shape_b)
		for shape in (shape_a, shape_b)
	}
	return overlapping_ids == {shape.id for shape in shapes}


def generate_challenge(
	*,
	minimum_shapes: int = 4,
	maximum_shapes: int = 5,
	canvas_size: int = 400,
	seed: int | None = None,
	max_attempts: int = 200,
) -> CaptchaChallenge:
	"""Create a random stack of distinct, overlapping shapes.

	Shapes are placed randomly and regenerated (up to ``max_attempts``)
	until every shape overlaps at least one other shape, so the
	transparent, overlapping-depth visual effect is always present.
	"""
	if not 2 <= minimum_shapes <= maximum_shapes <= min(len(SHAPE_TYPES), len(COLORS)):
		raise ValueError("shape count must be between 2 and the available distinct shapes/colors")
	if canvas_size < 100:
		raise ValueError("canvas_size must be at least 100")

	generator = random.Random(seed)
	count = generator.randint(minimum_shapes, maximum_shapes)
	margin = 60

	for _ in range(max_attempts):
		kinds = generator.sample(SHAPE_TYPES, count)
		colors = generator.sample(COLORS, count)
		depth_order = list(range(count))
		generator.shuffle(depth_order)

		shapes = tuple(
			Shape(
				id=str(uuid4()),
				kind=kind,
				color=color,
				x=generator.randint(margin, canvas_size - margin),
				y=generator.randint(margin, canvas_size - margin),
				size=generator.randint(90, 150),
				z_index=z_index,
			)
			for kind, color, z_index in zip(kinds, colors, depth_order)
		)
		if _has_meaningful_overlap(shapes):
			return CaptchaChallenge(id=token_urlsafe(16), shapes=shapes, canvas_size=canvas_size)

	# Extremely unlikely with the default parameters, but fail loudly rather
	# than silently returning a non-overlapping challenge.
	raise RuntimeError("could not generate an overlapping shape layout; try a larger canvas_size")
