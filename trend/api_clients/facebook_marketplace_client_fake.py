from typing import List
from datetime import datetime
from .base import BaseMarketplaceClient
from ..models import Listing


class FacebookMarketplaceClientFake(BaseMarketplaceClient):
    site_name = "facebook_marketplace"

    def search(self, query, min_price=None, max_price=None, limit=50, **kwargs):
        # simulating some specific car listings to show off the price history chart
        print("DEBUG: using fake FB marketplace data")

        # hardcoded snapshots to demo price drops
        data = [
            # Z4M in LA - dropping price
            {"id": "fb-bmw-z4m-1-jan", "title": "2007 BMW Z4 M Coupe · Manual · 120k miles", "price": 22000, "date": "2025-01-15T12:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-1"},
            {"id": "fb-bmw-z4m-1-feb", "title": "2007 BMW Z4 M Coupe · Manual · 120k miles", "price": 20900, "date": "2025-02-10T12:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-1"},
            {"id": "fb-bmw-z4m-1-mar", "title": "2007 BMW Z4 M Coupe · Manual · 120k miles", "price": 19950, "date": "2025-03-05T12:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-1"},

            # X5 diesel - sitting for a while
            {"id": "fb-bmw-x5d-1-dec", "title": "2010 BMW X5 xDrive35d · Diesel · 150k miles", "price": 11500, "date": "2024-12-01T11:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-x5d-1"},
            {"id": "fb-bmw-x5d-1-jan", "title": "2010 BMW X5 xDrive35d · Diesel · 150k miles", "price": 10800, "date": "2025-01-10T11:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-x5d-1"},
            {"id": "fb-bmw-x5d-1-feb", "title": "2010 BMW X5 xDrive35d · Diesel · 150k miles", "price": 9999, "date": "2025-02-20T11:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-x5d-1"},

            # Another Z4 in SD
            {"id": "fb-bmw-z4m-2-jan", "title": "2007 BMW Z4 M Coupe · Manual · 98k miles", "price": 25500, "date": "2025-01-03T13:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-2"},
            {"id": "fb-bmw-z4m-2-mar", "title": "2007 BMW Z4 M Coupe · Manual · 98k miles", "price": 23900, "date": "2025-03-12T13:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-2"},
            {"id": "fb-bmw-z4m-2-apr", "title": "2007 BMW Z4 M Coupe · Manual · 98k miles", "price": 22900, "date": "2025-04-05T13:00:00", "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-2"},
        ]

        results = []
        for d in data:
            results.append(Listing(
                site="facebook_marketplace",
                listing_id=d["id"],
                title=d["title"],
                price=float(d["price"]),
                currency="USD",
                url=d["url"],
                brand="BMW",
                size=None,
                condition=None,
                image_url=None,
                created_at=datetime.fromisoformat(d["date"]),
            ))

        # basic filtering
        if query:
            q = query.lower()
            results = [r for r in results if q in r.title.lower() or "bmw" in q]

        return results
