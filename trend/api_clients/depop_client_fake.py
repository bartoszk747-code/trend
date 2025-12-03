from typing import List
from datetime import datetime, timedelta
import random

from .base import BaseMarketplaceClient
from ..models import Listing


class DepopClientFake(BaseMarketplaceClient):
    """
    A simulated client for Depop.
    This class mocks the behavior of a real Depop API client by generating
    randomized listings that follow Depop's typical item style (Y2K, vintage, etc.).
    Useful for testing the aggregator without hitting real endpoints.
    """
    site_name = "depop"

    def __init__(self):
        # No API keys or auth needed for the fake client
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
        Simulates a search on Depop.
        
        Args:
            query: The search query (e.g. "jeans", "top")
            min_price: Minimum price filter
            max_price: Maximum price filter
            category: Category filter
            limit: Number of fake results to generate
            
        Returns:
            A list of Listing objects populated with mock data.
        """

        # Print a warning so we know this isn't real data
        print("Using FAKE Depop data (simulated).")

        # Depop listings often have specific keywords like "Y2K", "Vintage", "90s"
        base_titles = [
            "Y2K {} Baby Tee",
            "Vintage {} Graphic Tee",
            "{} Cargo Pants",
            "90s {} Sweatshirt",
            "{} Mini Skirt",
            "Vintage {} Track Jacket",
        ]
        
        if category:
            if category == "tops":
                base_titles = ["Y2K {} Baby Tee", "Vintage {} Graphic Tee", "90s {} Sweatshirt", "{} Crop Top"]
            elif category == "bottoms":
                base_titles = ["{} Cargo Pants", "{} Mini Skirt", "Low Rise {} Jeans", "{} Baggy Jeans"]
            elif category == "footwear":
                base_titles = ["Chunky {} Sneakers", "{} Platform Boots", "{} Mary Janes"]
            elif category == "accessories":
                base_titles = ["{} Trucker Hat", "{} Shoulder Bag", "{} Sunglasses"]

        # Common brands found on Depop

        # Common brands found on Depop
        brands = [
            "Brandy Melville",
            "Nike",
            "Adidas",
            "Harley Davidson",
            "Juicy Couture",
            "No Brand",
        ]
        
        # Standard sizing
        sizes = ["XS", "S", "M", "L", "XL", "One Size"]
        
        # Depop condition descriptors
        conditions = [
            "Used - good",
            "Used - excellent",
            "New with tags",
            "New without tags",
        ]

        listings: List[Listing] = []

        # Loop to create 'limit' number of fake items
        for i in range(limit):
            # Randomly select attributes to make the data look varied
            title = random.choice(base_titles).format(query.capitalize())
            brand = random.choice(brands)
            size = random.choice(sizes)
            condition = random.choice(conditions)

            # Generate a random price, typically lower range for Depop
            price = random.randint(15, 120)
            
            # Randomize the listing date within the last month
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
                    image_url=None, # No real images available
                    created_at=created_at,
                )
            )

        return listings
