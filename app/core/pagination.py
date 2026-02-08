from dataclasses import dataclass


@dataclass(frozen=True)
class Pagination:
    """Pagination parameters for list queries."""

    page: int
    size: int

    @property
    def offset(self) -> int:
        """Return the SQL offset based on page and size."""
        return max(self.page - 1, 0) * self.size
