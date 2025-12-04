from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class DepopClientFake(BaseMarketplaceClient):
    site_name = "depop"

    def search(self, query, min_price=None, max_price=None, limit=20, **kwargs):
        # TODO: implement real scraping later
        print("generating fake depop items...")

        # y2k stuff usually
        templates = [
            "Y2K {} Baby Tee", "Vintage {} Graphic Tee", "{} Cargo Pants",
            "90s {} Sweatshirt", "{} Mini Skirt", "Vintage {} Track Jacket"
        ]

        brands = ["Brandy Melville", "Nike", "Adidas", "Harley Davidson", "Juicy Couture"]
        
        out = []
        for i in range(limit):
            t = random.choice(templates).format(query.capitalize())
            
            out.append(Listing(
                site="depop",
                listing_id=f"fake-depop-{i}",
                title=t,
                price=float(random.randint(15, 120)),
                currency="USD",
                url=f"https://www.depop.com/products/fake-depop-{i}/",
                brand=random.choice(brands),
                size=random.choice(["XS", "S", "M", "L", "XL", "One Size"]),
                condition=random.choice(["Used - good", "Used - excellent", "NWT"]),
                image_url=None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            ))

        return out
