from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class PoshmarkClientFake(BaseMarketplaceClient):
    site_name = "poshmark"

    def search(self, query, min_price=None, max_price=None, limit=20, **kwargs):
        #One we get the real API this would be different 
        print(f"DEBUG: returning fake poshmark results for {query}")

        titles = [
            "{} Midi Dress", "NWT {} Blazer", "{} Workout Set",
            "Oversized {} Sweater", "{} Lounge Set", "{} Trench Coat"
        ]
        
        #Popular brands we found on Poshmark
        brands = ["Aritzia", "Lululemon", "Free People", "Zara", "Madewell", "Anthropologie"]
        results = []
        for i in range(limit):
            # rndm price 25 to 250
            p = random.randint(25, 250)
            
            # rnd date last 60 days
            days_ago = random.randint(0, 60)
            dt = datetime.utcnow() - timedelta(days=days_ago)

           
           
            item = Listing(
                site="poshmark",
                listing_id=f"fake-posh-{i}",
                title=random.choice(titles).format(query.capitalize()),
                price=float(p),
                currency="USD",
                url=f"https://poshmark.com/listing/fake-posh-{i}",
                brand=random.choice(brands),
                size=random.choice(["XS", "S", "M", "L", "XL"]),
                condition=random.choice(["NWT", "NWOT", "Excellent", "Good"]),
                image_url=None,
                created_at=dt,
            )
            results.append(item)
        return results