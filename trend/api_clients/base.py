from abc import ABC, abstractmethod
from typing import List

from ..models import Listing


class BaseMarketplaceClient(ABC):
    """Abstract base class for marketplace clients (Grailed, Poshmark, Depop)."""

    site_name: str

    @abstractmethod
    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        size: str | None = None,
        brand: str | None = None,
        limit: int = 40,
    ) -> List[Listing]:
        """Return a list of normalized Listing objects for this marketplace."""
        raise NotImplementedError
