"""Core data generation for the Confident Captcha prototype.

The renderer and web API can build on these records without needing to know
how a challenge was randomized.
"""
from PIL import Image, ImageDraw
from dataclasses import dataclass
from secrets import token_urlsafe
from typing import Final
from uuid import UUID, uuid4
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

	id: UUID
	kind: str
	color: str
	x: int
	y: int
	size: int
	z_index: int


@dataclass(frozen=True, slots=True)
class CaptchaChallenge:
	"""Server-side challenge data used to render and validate a CAPTCHA."""

	id: str
	shapes: tuple[Shape, ...]


def generate_challenge(
	*,
	minimum_shapes: int = 5,
	maximum_shapes: int = 7,
	canvas_size: int = 400,
	seed: int | None = None,
) -> CaptchaChallenge:
	"""Create a random stack of distinct shapes with known depth ordering."""

	if not 1 <= minimum_shapes <= maximum_shapes <= min(len(SHAPE_TYPES), len(COLORS)):
		raise ValueError("shape count must be between 1 and the available distinct shapes/colors")
	if canvas_size < 100:
		raise ValueError("canvas_size must be at least 100")

	generator = random.Random(seed)
	count = generator.randint(minimum_shapes, maximum_shapes)
	kinds = generator.sample(SHAPE_TYPES, count)
	colors = generator.sample(COLORS, count)
	depth_order = list(range(count))
	generator.shuffle(depth_order)

	shapes = tuple(
		Shape(
			id=uuid4(),
			kind=kind,
			color=color,
			x=generator.randint(40, canvas_size - 40),
			y=generator.randint(40, canvas_size - 40),
			size=generator.randint(70, 130),
			z_index=z_index,
		)
		for kind, color, z_index in zip(kinds, colors, depth_order)
	)
	return CaptchaChallenge(id=token_urlsafe(16), shapes=shapes)
