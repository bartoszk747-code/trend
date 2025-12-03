from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class PoshmarkClientFake(BaseMarketplaceClient):
    site_name = "poshmark"

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
        Fake Poshmark client.
        Generates realistic Poshmark-style listings.
        """

        print("⚠ Using FAKE Poshmark data (simulated).")

        base_titles = [
            "{} Midi Dress",
            "NWT {} Blazer",
            "{} Workout Set",
            "Oversized {} Sweater",
            "{} Lounge Set",
            "{} Trench Coat",
        ]

        brands = [
            "Aritzia",
            "Lululemon",
            "Free People",
            "Zara",
            "Madewell",
            "Anthropologie",
            "No Brand",
        ]
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        conditions = [
            "New with tags",
            "New without tags",
            "Excellent used condition",
            "Good used condition",
        ]

        listings: List[Listing] = []

        for i in range(limit):
            title = random.choice(base_titles).format(query.capitalize())
            brand = random.choice(brands)
            size = random.choice(sizes)
            condition = random.choice(conditions)

            price = random.randint(25, 250)
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 60))

            listings.append(
                Listing(
                    site="poshmark",
                    listing_id=f"fake-posh-{i}",
                    title=title,
                    price=float(price),
                    currency="USD",
                    url=f"https://poshmark.com/listing/fake-posh-{i}",
                    brand=brand,
                    size=size,
                    condition=condition,
                    image_url=None,
                    created_at=created_at,
                )
            )

        return listings