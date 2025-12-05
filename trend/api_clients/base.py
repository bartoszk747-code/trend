from abc import ABC, abstractmethod
from typing import List

from ..models import Listing


class BaseMarketplaceClient(ABC):
    """Base for various clients (Grailed, Poshmark, Depop)."""
 # name of the site.
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
        """Return a list of normalized listing objects for the chosen marketplace."""
        #the subclass can't overide this
        raise NotImplementedError
