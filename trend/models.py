from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal

SiteName = Literal["grailed", "poshmark", "depop"]


@dataclass
class Listing:
    site: SiteName
    listing_id: str
    title: str
    price: float
    currency: str
    url: str

    brand: Optional[str] = None
    size: Optional[str] = None
    condition: Optional[str] = None
    image_url: Optional[str] = None

    created_at: Optional[datetime] = None
    scraped_at: datetime = datetime.utcnow()
