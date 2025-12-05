from .models import Listing
def notify_new_listing(listing: Listing):
    print(f"[NEW LISTING] {listing.title} - {listing.price} {listing.currency}")
    print(f"URL: {listing.url}")