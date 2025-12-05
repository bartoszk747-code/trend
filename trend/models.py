from dataclasses import dataclass



from datetime import datetime

from typing import Optional, Literal

SiteName = Literal["grailed", 
"poshmark", "depop"]

@dataclass
class Listing:
    site: SiteName # market source
    listing_id: str # ID wed use to identify(fake for now)
    title: str 
    price: float
    currency: str 
    #multiple(USD</EUR/GBP etc)
    url: str
    brand: Optional[str] = None

    size: Optional[str] = None
    condition: Optional[str] = None
    image_url: Optional[str] = None

    created_at: Optional[datetime] = None
    scraped_at: datetime = datetime.utcnow()
