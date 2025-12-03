from typing import List
from datetime import datetime

from grailed_api import GrailedAPIClient
from grailed_api.enums import Markets

from .base import BaseMarketplaceClient
from ..models import Listing


class GrailedClient(BaseMarketplaceClient):
    """
    Client for interacting with the Grailed marketplace.
    Wraps the unofficial grailed_api library to search for listings.
    """
    site_name = "grailed"

    def __init__(self):
        # Initialize the underlying API client
        self._client = GrailedAPIClient()

    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        size: str | None = None,
        brand: str | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> List[Listing]:
        """
        Search for items on Grailed.
        
        Args:
            query: Search text
            min_price: Minimum price in USD
            max_price: Maximum price in USD
            size: Size filter (not fully implemented in mapping yet)
            brand: Brand name to filter by
            category: Category filter (e.g. "tops", "bottoms")
            limit: Max results to return
        """

        # Default price range if not specified
        price_from = int(min_price or 0)
        price_to = int(max_price or 999999)

        # Construct the search query. If we have a brand, prepend it to help relevance.
        # If we have a category, append it to the query to help narrow down results.
        search_parts = []
        if brand:
            search_parts.append(brand)
        search_parts.append(query)
        if category:
            search_parts.append(category)
        
        search_query = " ".join(search_parts)
        
        # The grailed_api expects a list of designers if we want to filter by brand specifically
        designers = [brand] if brand else ()

        # Call the Grailed API
        # We target both BASIC and GRAILED markets to get a wider range of items.
        products = self._client.find_products(
            sold=False,
            on_sale=True,
            query_search=search_query,
            page=1,
            hits_per_page=limit,
            price_from=price_from,
            price_to=price_to,
            designers=designers,
            markets=(Markets.BASIC, Markets.GRAILED),
            verbose=False,
        )

        listings: List[Listing] = []

        for p in products:
            # Extract fields with fallbacks because the API response can be inconsistent
            listing_id = str(p.get("id") or p.get("objectID") or "")
            title = p.get("title") or p.get("name") or "Unknown"
            
            # Price comes in as an integer usually (cents? or whole dollars?), assuming whole dollars based on usage
            price = float(p.get("price") or 0)
            currency = p.get("currency") or "USD"
            url = p.get("url") or ""

            # Try to find brand and size info from various possible keys
            brand_name = p.get("brand_name") or p.get("designer_name")
            size_name = p.get("size") or p.get("size_name")
            condition_name = p.get("condition") or p.get("condition_name")
            
            # Photos might be under image_url or photo_url
            image_url = p.get("image_url") or p.get("photo_url")

            # Parse the creation date if available
            created_raw = p.get("created_at")
            created_at = None
            if created_raw:
                try:
                    # Handle ISO format with Z for UTC
                    created_at = datetime.fromisoformat(
                        created_raw.replace("Z", "+00:00")
                    )
                except Exception:
                    # If date parsing fails, just leave it as None
                    created_at = None

            listings.append(
                Listing(
                    site="grailed",
                    listing_id=listing_id,
                    title=title,
                    price=price,
                    currency=currency,
                    url=url,
                    brand=brand_name,
                    size=size_name,
                    condition=condition_name,
                    image_url=image_url,
                    created_at=created_at,
                )
            )

        return listings
