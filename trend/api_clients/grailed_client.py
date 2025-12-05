#using unofficial grailed API that we found 
from typing import List
from datetime import datetime

from grailed_api import GrailedAPIClient
from grailed_api.enums import Markets

from .base import BaseMarketplaceClient
from ..models import Listing


#Grailed client
class GrailedClient(BaseMarketplaceClient):
    site_name = "grailed"

    def __init__(self):
        self._client = GrailedAPIClient()

    def search(self, query, min_price=None, max_price=None, size=None, brand=None, limit=20):
        # using the unofficial api wrapper
        # Need to figure out why it doesn't display sometimes 
        p_min = int(min_price or 0)
        p_max = int(max_price or 999999)

        q = query
        if brand:
            q = f"{brand} {query}"

        # fetch from grailed
        res = self._client.find_products(
            sold=False,
            on_sale=True,
            query_search=q,
            page=1,
            hits_per_page=limit,
            price_from=p_min,
            price_to=p_max,
            designers=[brand] if brand else (),
            markets=(Markets.BASIC, Markets.GRAILED),
            verbose=False,
        )

        out = []
        for item in res:
            # grailed api data is inconsistent can't always be read 
            lid = str(item.get("id") or item.get("objectID") or "")
            
            
            #Parse
            created = None
            if raw_date := item.get("created_at"):
                try:
                    created = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                except:
                    pass

            out.append(Listing(
                site="grailed",
                listing_id=lid,
                title=item.get("title") or item.get("name") or "Unknown",
                price=float(item.get("price") or 0),
                currency=item.get("currency") or "USD",
                url=item.get("url") or "",
                brand=item.get("brand_name") or item.get("designer_name"),
                size=item.get("size") or item.get("size_name"),
                condition=item.get("condition") or item.get("condition_name"),
                image_url=item.get("image_url") or item.get("photo_url"),
                created_at=created,
            ))

        return out
