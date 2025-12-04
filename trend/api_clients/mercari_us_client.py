from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class MercariUSClient(BaseMarketplaceClient):
    site_name = "mercari_us"

    def search(self, query, min_price=None, max_price=None, limit=10, **kwargs):
        # fake data generator for mercari
        print(f"DEBUG: getting fake mercari listings for {query}")

        titles = [
            "Vintage {} Jacket", "{} Puffer Jacket", "Y2K {} Zip-Up Hoodie",
            "{} Workwear Coat", "Oversized {} Fleece"
        ]

        brands = ["Carhartt", "Nike", "Adidas", "The North Face", "Columbia", "Patagonia"]

        items = []
        for i in range(limit):
            t = random.choice(titles).format(query.capitalize())
            
            # random price/date
            p = random.randint(20, 250)
            dt = datetime.utcnow() - timedelta(days=random.randint(0, 30))

            items.append(Listing(
                site="mercari_us",
                listing_id=f"fake-mus-{i}",
                title=t,
                price=float(p),
                currency="USD",
                url=f"https://www.mercari.com/us/item/fake-mus-{i}/",
                brand=random.choice(brands),
                size=random.choice(["XS", "S", "M", "L", "XL", "XXL"]),
                condition=random.choice(["New", "Good", "Fair", "Used"]),
                image_url=None,
                created_at=dt,
            ))

        return items
