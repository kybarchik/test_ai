from dataclasses import dataclass


@dataclass(slots=True)
class Pagination:
    """Pagination metadata for templates."""

    page: int
    per_page: int
    total: int

    @property
    def total_pages(self) -> int:
        """Return total pages, at least 1."""
        if self.total <= 0:
            return 1
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def offset(self) -> int:
        """Return the SQL offset for the current page."""
        return (self.page - 1) * self.per_page


def clamp_pagination(page: int, per_page: int, max_per_page: int = 50) -> tuple[int, int]:
    """Normalize pagination values to safe defaults."""
    safe_page = max(page, 1)
    safe_per_page = min(max(per_page, 1), max_per_page)
    return safe_page, safe_per_page
