from typing import List
from datetime import datetime

from grailed_api import GrailedAPIClient
from grailed_api.enums import Markets

from .base import BaseMarketplaceClient
from ..models import Listing


class GrailedClient(BaseMarketplaceClient):
    site_name = "grailed"

    def __init__(self):
        self._client = GrailedAPIClient()

    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        size: str | None = None,
        brand: str | None = None,
        limit: int = 20,
    ) -> List[Listing]:

        price_from = int(min_price or 0)
        price_to = int(max_price or 999999)

        products = self._client.find_products(
            sold=False,
            on_sale=True,
            query_search=query if not brand else f"{brand} {query}",
            page=1,
            hits_per_page=limit,
            price_from=price_from,
            price_to=price_to,
            designers=[brand] if brand else (),
            markets=(Markets.BASIC, Markets.GRAILED),
            verbose=False,
        )

        listings: List[Listing] = []

        for p in products:
            listing_id = str(p.get("id") or p.get("objectID") or "")
            title = p.get("title") or p.get("name") or "Unknown"
            price = float(p.get("price") or 0)
            currency = p.get("currency") or "USD"
            url = p.get("url") or ""

            brand_name = p.get("brand_name") or p.get("designer_name")
            size_name = p.get("size") or p.get("size_name")
            condition_name = p.get("condition") or p.get("condition_name")
            image_url = p.get("image_url") or p.get("photo_url")

            created_raw = p.get("created_at")
            created_at = None
            if created_raw:
                try:
                    created_at = datetime.fromisoformat(
                        created_raw.replace("Z", "+00:00")
                    )
                except Exception:
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
