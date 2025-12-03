from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class MercariUSClient(BaseMarketplaceClient):
    site_name = "mercari_us"

    def __init__(self):
        pass

    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 10,
        **kwargs
    ) -> List[Listing]:
        """
        Fake / simulated Mercari US client.
        Generates realistic-looking demo data so the app behaves
        as if it's talking to Mercari US.
        """

        print("⚠ Using FAKE Mercari US data (simulated).")

        base_titles = [
            "Vintage {} Jacket",
            "{} Puffer Jacket",
            "Y2K {} Zip-Up Hoodie",
            "{} Workwear Coat",
            "Oversized {} Fleece",
        ]

        brands = [
            "Carhartt",
            "Nike",
            "Adidas",
            "The North Face",
            "Columbia",
            "Patagonia",
            "No Brand",
        ]

        sizes = ["XS", "S", "M", "L", "XL", "XXL"]

        conditions = [
            "New with tags",
            "New without tags",
            "Good",
            "Fair",
            "Used",
        ]

        listings: List[Listing] = []

        for i in range(limit):
            title = random.choice(base_titles).format(query.capitalize())
            brand = random.choice(brands)
            size = random.choice(sizes)
            condition = random.choice(conditions)

            price = random.randint(20, 250)  # USD
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))

            listings.append(
                Listing(
                    site="mercari_us",
                    listing_id=f"fake-mus-{i}",
                    title=title,
                    price=float(price),
                    currency="USD",
                    url=f"https://www.mercari.com/us/item/fake-mus-{i}/",
                    brand=brand,
                    size=size,
                    condition=condition,
                    image_url=None,
                    created_at=created_at,
                )
            )

        return listings
