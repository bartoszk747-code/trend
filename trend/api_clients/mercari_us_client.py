from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class MercariUSClient(BaseMarketplaceClient):
    """
    Client for interacting with Mercari US.
    Currently, this is a simulation/mock client because we don't have a public API for Mercari.
    It generates realistic-looking listings for development and testing purposes.
    """
    site_name = "mercari_us"

    def __init__(self):
        # No authentication needed for the fake client
        pass

    def search(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        category: str | None = None,
        limit: int = 10,
        **kwargs
    ) -> List[Listing]:
        """
        Simulates a search on Mercari US.
        
        Args:
            query: The search term (e.g. "jacket")
            min_price: Minimum price filter
            max_price: Maximum price filter
            category: Category filter
            limit: Number of fake results to generate
            
        Returns:
            A list of Listing objects with generated data.
        """

        # Warn the developer that this is not real data
        print("Using FAKE Mercari US data (simulated).")

        # Templates for generating realistic titles
        base_titles = [
            "Vintage {} Jacket",
            "{} Puffer Jacket",
            "Y2K {} Zip-Up Hoodie",
            "{} Workwear Coat",
            "Oversized {} Fleece",
        ]
        
        if category:
             # Adjust titles slightly based on category if provided
            if category == "tops":
                base_titles = ["{} T-Shirt", "{} Hoodie", "{} Sweater", "Vintage {} Tee"]
            elif category == "bottoms":
                base_titles = ["{} Jeans", "{} Cargo Pants", "{} Shorts", "Vintage {} Denims"]
            elif category == "footwear":
                base_titles = ["{} Sneakers", "{} Boots", "{} Loafers", "Used {} Shoes"]
            elif category == "accessories":
                base_titles = ["{} Hat", "{} Bag", "{} Belt", "{} Wallet"]

        # Common brands to populate the listings
        brands = [
            "Carhartt",
            "Nike",
            "Adidas",
            "The North Face",
            "Columbia",
            "Patagonia",
            "No Brand",
        ]

        # Standard sizing options
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]

        # Typical item conditions found on marketplaces
        conditions = [
            "New with tags",
            "New without tags",
            "Good",
            "Fair",
            "Used",
        ]

        listings: List[Listing] = []

        # Generate 'limit' number of fake listings
        for i in range(limit):
            # Randomly assemble listing details
            title = random.choice(base_titles).format(query.capitalize())
            brand = random.choice(brands)
            size = random.choice(sizes)
            condition = random.choice(conditions)

            # Generate a random price within a reasonable range
            price = random.randint(20, 250)  # USD
            
            # Randomize the creation date to be within the last 30 days
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
                    image_url=None, # No real images for fake data
                    created_at=created_at,
                )
            )

        return listings
