from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class PoshmarkClientFake(BaseMarketplaceClient):
    """
    A simulated client for Poshmark.
    Since we don't have a public API for Poshmark, this class generates
    mock data that resembles real Poshmark listings for testing and development.
    """
    site_name = "poshmark"

    def __init__(self):
        # No setup required for the fake client
        pass

    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        category: str | None = None,
        limit: int = 20,
        **kwargs,
    ) -> List[Listing]:
        """
        Simulates a search on Poshmark.
        
        Args:
            query: Search keywords (e.g. "dress", "boots")
            min_price: Minimum price filter
            max_price: Maximum price filter
            category: Category filter
            limit: Number of fake results to return
            
        Returns:
            List of Listing objects with generated data.
        """

        # Log that we are using fake data so it's obvious in the console
        print("⚠ Using FAKE Poshmark data (simulated).")

        # Templates for generating titles that sound like Poshmark listings
        base_titles = [
            "{} Midi Dress",
            "NWT {} Blazer",
            "{} Workout Set",
            "Oversized {} Sweater",
            "{} Lounge Set",
            "{} Trench Coat",
        ]
        
        if category:
            if category == "tops":
                base_titles = ["NWT {} Blazer", "Oversized {} Sweater", "{} Blouse", "{} Tank Top"]
            elif category == "bottoms":
                base_titles = ["{} Jeans", "{} Leggings", "{} Skirt", "{} Trousers"]
            elif category == "footwear":
                base_titles = ["{} Boots", "{} Heels", "{} Sandals", "{} Sneakers"]
            elif category == "accessories":
                base_titles = ["{} Handbag", "{} Necklace", "{} Scarf", "{} Belt"]

        # Popular brands often found on Poshmark

        # Popular brands often found on Poshmark
        brands = [
            "Aritzia",
            "Lululemon",
            "Free People",
            "Zara",
            "Madewell",
            "Anthropologie",
            "No Brand",
        ]
        
        # Standard sizes
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        
        # Poshmark specific condition terminology
        conditions = [
            "New with tags",
            "New without tags",
            "Excellent used condition",
            "Good used condition",
        ]

        listings: List[Listing] = []

        # Generate the requested number of fake listings
        for i in range(limit):
            # Randomly pick attributes to create a diverse result set
            title = random.choice(base_titles).format(query.capitalize())
            brand = random.choice(brands)
            size = random.choice(sizes)
            condition = random.choice(conditions)

            # Generate a random price
            price = random.randint(25, 250)
            
            # Randomize creation date (within last 60 days)
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
                    image_url=None, # Placeholder for image URL
                    created_at=created_at,
                )
            )

        return listings