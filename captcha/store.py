"""In-memory, single-use challenge store.

This is a classroom demo, not a production service: challenges live only
for the lifetime of the process, are removed as soon as they are
verified (pass or fail), and there is no expiry/cleanup timer.
"""
from dataclasses import dataclass
from threading import Lock

from .renderer import RenderedChallenge


@dataclass(frozen=True, slots=True)
class StoredChallenge:
	"""What the server remembers about an outstanding challenge."""

	correct_shape_id: str
	rendered: RenderedChallenge


class ChallengeStore:
	"""Thread-safe in-memory map of challenge id -> stored challenge."""

	def __init__(self) -> None:
		self._lock = Lock()
		self._challenges: dict[str, StoredChallenge] = {}

	def put(self, challenge_id: str, stored: StoredChallenge) -> None:
		with self._lock:
			self._challenges[challenge_id] = stored

	def pop(self, challenge_id: str) -> StoredChallenge | None:
		"""Remove and return a stored challenge; single-use, so pop not get."""
		with self._lock:
			return self._challenges.pop(challenge_id, None)
