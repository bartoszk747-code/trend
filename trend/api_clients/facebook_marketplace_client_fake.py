from typing import List
from datetime import datetime
from .base import BaseMarketplaceClient
from ..models import Listing


class FacebookMarketplaceClientFake(BaseMarketplaceClient):
    site_name = "facebook_marketplace"

    def __init__(self):
        pass

    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 50,
        **kwargs,
    ) -> List[Listing]:
        """
        Fake Facebook Marketplace client.

        Specifically simulates a couple of BMW listings over several months
        with price changes, so you can demo price-drop & trend features.
        """

        print("⚠ Using FAKE Facebook Marketplace data (simulated).")

        # Hard-coded time series for two cars
        # Dates are just example ISO strings; you'll use created_at for trend graphs.

        snapshots = [
            # 2007 BMW Z4M Coupe – price dropping over time
            {
                "id": "fb-bmw-z4m-1-jan",
                "title": "2007 BMW Z4 M Coupe · Manual · 120k miles",
                "price": 22000,
                "date": "2025-01-15T12:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-1",
                "location": "Los Angeles, CA",
            },
            {
                "id": "fb-bmw-z4m-1-feb",
                "title": "2007 BMW Z4 M Coupe · Manual · 120k miles",
                "price": 20900,
                "date": "2025-02-10T12:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-1",
                "location": "Los Angeles, CA",
            },
            {
                "id": "fb-bmw-z4m-1-mar",
                "title": "2007 BMW Z4 M Coupe · Manual · 120k miles",
                "price": 19950,
                "date": "2025-03-05T12:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-1",
                "location": "Los Angeles, CA",
            },

            # 2010 BMW X5 xDrive35d – shows longer time on market
            {
                "id": "fb-bmw-x5d-1-dec",
                "title": "2010 BMW X5 xDrive35d · Diesel · 150k miles",
                "price": 11500,
                "date": "2024-12-01T11:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-x5d-1",
                "location": "Anaheim, CA",
            },
            {
                "id": "fb-bmw-x5d-1-jan",
                "title": "2010 BMW X5 xDrive35d · Diesel · 150k miles",
                "price": 10800,
                "date": "2025-01-10T11:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-x5d-1",
                "location": "Anaheim, CA",
            },
            {
                "id": "fb-bmw-x5d-1-feb",
                "title": "2010 BMW X5 xDrive35d · Diesel · 150k miles",
                "price": 9999,
                "date": "2025-02-20T11:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-x5d-1",
                "location": "Anaheim, CA",
            },

            # Another Z4 listing in a different state
            {
                "id": "fb-bmw-z4m-2-jan",
                "title": "2007 BMW Z4 M Coupe · Manual · 98k miles",
                "price": 25500,
                "date": "2025-01-03T13:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-2",
                "location": "San Diego, CA",
            },
            {
                "id": "fb-bmw-z4m-2-mar",
                "title": "2007 BMW Z4 M Coupe · Manual · 98k miles",
                "price": 23900,
                "date": "2025-03-12T13:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-2",
                "location": "San Diego, CA",
            },
            {
                "id": "fb-bmw-z4m-2-apr",
                "title": "2007 BMW Z4 M Coupe · Manual · 98k miles",
                "price": 22900,
                "date": "2025-04-05T13:00:00",
                "url": "https://www.facebook.com/marketplace/item/fb-bmw-z4m-2",
                "location": "San Diego, CA",
            },
        ]

        listings: List[Listing] = []

        for snap in snapshots:
            created_at = datetime.fromisoformat(snap["date"])

            listings.append(
                Listing(
                    site="facebook_marketplace",
                    listing_id=snap["id"],
                    title=snap["title"],
                    price=float(snap["price"]),
                    currency="USD",
                    url=snap["url"],
                    brand="BMW",
                    size=None,
                    condition=None,
                    image_url=None,
                    created_at=created_at,
                )
            )

        # filtering by query if you type "BMW" or "Z4" or "X5"
        if query:
            q = query.lower()
            listings = [
                l for l in listings
                if q in l.title.lower()
                or q in (l.brand or "").lower()
            ]

        return listings
