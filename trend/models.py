from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal

SiteName = Literal["grailed", "poshmark", "depop"]

@dataclass
class Listing:
    site: SiteName # market source
    listing_id: str # internal ID present(simulated)
    title: str 
    price: float
    currency: str #multiple?
    url: str
    brand: Optional[str] = None
    size: Optional[str] = None
    condition: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    scraped_at: datetime = datetime.utcnow()
