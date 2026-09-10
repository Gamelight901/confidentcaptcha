"""Answer validation for the Confident Captcha challenge."""
from dataclasses import dataclass

from .renderer import shape_id_at
from .store import StoredChallenge


@dataclass(frozen=True, slots=True)
class VerificationResult:
	success: bool


def verify_click(stored: StoredChallenge, x: int, y: int) -> VerificationResult:
	"""Check whether the click at (x, y) lands on the correct shape.

	Resolves the click through the rendered hit mask so the *visible*,
	topmost shape at that pixel is what gets checked, not merely a shape
	whose bounding box happens to contain the point.
	"""
	clicked_shape_id = shape_id_at(stored.rendered, x, y)
	return VerificationResult(success=clicked_shape_id == stored.correct_shape_id)
