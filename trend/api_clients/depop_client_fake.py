from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class DepopClientFake(BaseMarketplaceClient):
    site_name = "depop"

    def __init__(self):
        pass

    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 20,
        **kwargs,
    ) -> List[Listing]:
        """
        Fake Depop client.
        Generates realistic Depop-style listings.
        """

        print("⚠ Using FAKE Depop data (simulated).")

        base_titles = [
            "Y2K {} Baby Tee",
            "Vintage {} Graphic Tee",
            "{} Cargo Pants",
            "90s {} Sweatshirt",
            "{} Mini Skirt",
            "Vintage {} Track Jacket",
        ]

        brands = [
            "Brandy Melville",
            "Nike",
            "Adidas",
            "Harley Davidson",
            "Juicy Couture",
            "No Brand",
        ]
        sizes = ["XS", "S", "M", "L", "XL", "One Size"]
        conditions = [
            "Used - good",
            "Used - excellent",
            "New with tags",
            "New without tags",
        ]

        listings: List[Listing] = []

        for i in range(limit):
            title = random.choice(base_titles).format(query.capitalize())
            brand = random.choice(brands)
            size = random.choice(sizes)
            condition = random.choice(conditions)

            price = random.randint(15, 120)
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))

            listings.append(
                Listing(
                    site="depop",
                    listing_id=f"fake-depop-{i}",
                    title=title,
                    price=float(price),
                    currency="USD",
                    url=f"https://www.depop.com/products/fake-depop-{i}/",
                    brand=brand,
                    size=size,
                    condition=condition,
                    image_url=None,
                    created_at=created_at,
                )
            )

        return listings
