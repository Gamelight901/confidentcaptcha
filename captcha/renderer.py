"""Rendering engine for the Confident Captcha challenge.

Draws every shape in a challenge as a semi-transparent layer, composited
bottom-to-top by depth (``z_index``), and produces a matching per-pixel
"hit mask" so a click can be resolved to the shape that is actually
visible (topmost) at that pixel, not just the shape whose bounding box
contains it.
"""
from dataclasses import dataclass
from io import BytesIO
from typing import Final
import math

from PIL import Image, ImageColor, ImageDraw

from .generator import CaptchaChallenge, Shape

SHAPE_ALPHA: Final[int] = 170
BACKGROUND_COLOR: Final[tuple[int, int, int, int]] = (255, 255, 255, 255)


@dataclass(frozen=True, slots=True)
class RenderedChallenge:
	"""A rendered challenge: the composited PNG bytes and a hit mask."""

	png_bytes: bytes
	# hit_mask[y][x] is the shape id visible at that pixel, or None for background.
	hit_mask: tuple[tuple[str | None, ...], ...]


def _regular_polygon_points(
	cx: float, cy: float, radius: float, sides: int, rotation_deg: float = -90
) -> list[tuple[float, float]]:
	"""Return the vertices of a regular polygon centered at (cx, cy)."""
	rotation = math.radians(rotation_deg)
	step = 2 * math.pi / sides
	return [
		(cx + radius * math.cos(rotation + i * step), cy + radius * math.sin(rotation + i * step))
		for i in range(sides)
	]


def _star_points(
	cx: float, cy: float, outer_radius: float, inner_radius: float, points: int = 5
) -> list[tuple[float, float]]:
	"""Return the vertices of a symmetric star centered at (cx, cy)."""
	rotation = math.radians(-90)
	step = math.pi / points
	vertices = []
	for i in range(points * 2):
		radius = outer_radius if i % 2 == 0 else inner_radius
		angle = rotation + i * step
		vertices.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
	return vertices


def _draw_shape(draw: ImageDraw.ImageDraw, shape: Shape, fill: tuple[int, ...]) -> None:
	"""Draw ``shape`` onto ``draw`` using ``fill`` (an RGBA or single-value color)."""
	half = shape.size / 2
	if shape.kind == "circle":
		draw.ellipse((shape.x - half, shape.y - half, shape.x + half, shape.y + half), fill=fill)
	elif shape.kind == "square":
		draw.rectangle((shape.x - half, shape.y - half, shape.x + half, shape.y + half), fill=fill)
	elif shape.kind == "diamond":
		draw.polygon(_regular_polygon_points(shape.x, shape.y, half, 4), fill=fill)
	elif shape.kind == "triangle":
		draw.polygon(_regular_polygon_points(shape.x, shape.y, half, 3), fill=fill)
	elif shape.kind == "pentagon":
		draw.polygon(_regular_polygon_points(shape.x, shape.y, half, 5), fill=fill)
	elif shape.kind == "hexagon":
		draw.polygon(_regular_polygon_points(shape.x, shape.y, half, 6), fill=fill)
	elif shape.kind == "star":
		draw.polygon(_star_points(shape.x, shape.y, half, half * 0.4), fill=fill)
	else:
		raise ValueError(f"unknown shape kind: {shape.kind!r}")


def render_challenge(challenge: CaptchaChallenge) -> RenderedChallenge:
	"""Render a challenge to a composited PNG plus a per-pixel hit mask."""
	size = challenge.canvas_size
	base = Image.new("RGBA", (size, size), BACKGROUND_COLOR)
	mask = Image.new("L", (size, size), 0)
	mask_draw = ImageDraw.Draw(mask)

	# Assign each shape a stable 1-based index (0 stays reserved for "background").
	shapes_by_id = {shape.id: index + 1 for index, shape in enumerate(challenge.shapes)}
	ordered_shapes = sorted(challenge.shapes, key=lambda shape: shape.z_index)

	for shape in ordered_shapes:
		layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
		layer_draw = ImageDraw.Draw(layer)
		rgb = ImageColor.getrgb(shape.color)
		_draw_shape(layer_draw, shape, fill=(*rgb, SHAPE_ALPHA))
		base = Image.alpha_composite(base, layer)
		_draw_shape(mask_draw, shape, fill=shapes_by_id[shape.id])

	buffer = BytesIO()
	base.convert("RGB").save(buffer, format="PNG")

	index_to_id = {index: shape_id for shape_id, index in shapes_by_id.items()}
	mask_pixels = mask.load()
	hit_mask = tuple(
		tuple(index_to_id.get(mask_pixels[x, y]) for x in range(size)) for y in range(size)
	)
	return RenderedChallenge(png_bytes=buffer.getvalue(), hit_mask=hit_mask)


def shape_id_at(rendered: RenderedChallenge, x: int, y: int) -> str | None:
	"""Return the id of the shape visible at pixel (x, y), or None."""
	if 0 <= y < len(rendered.hit_mask) and 0 <= x < len(rendered.hit_mask[0]):
		return rendered.hit_mask[y][x]
	return None
