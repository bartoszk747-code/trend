"""
Demo script to showcase the functionality of various marketplace clients.
This script initializes the database and runs search queries across different platforms
(Grailed, Mercari, Depop, Poshmark, Facebook Marketplace) to demonstrate data retrieval.
"""

from trend.api_clients.grailed_client import GrailedClient
from trend.api_clients.mercari_us_client import MercariUSClient
from trend.api_clients.depop_client_fake import DepopClientFake
from trend.api_clients.poshmark_client_fake import PoshmarkClientFake
from trend.api_clients.facebook_marketplace_client_fake import FacebookMarketplaceClientFake
from trend.db import init_db


def main():
    """
    Main execution function.
    Runs a sequence of searches on different marketplaces and prints the results.
    """
    print("Starting the demo script...")

    # Ensure the database is set up before we begin (though we aren't saving results here yet)
    init_db()

    # --- GRAILED ---
    # Real API client (wrapper around unofficial API)
    print("\n--- Searching Grailed (Real API) ---")
    client = GrailedClient()
    results = client.search("jacket", limit=3)

    print(f"Found {len(results)} items on Grailed:")
    for r in results:
        print("-" * 20)
        print(f"Title: {r.title}")
        print(f"Price: {r.price} {r.currency}")
        print(f"Link:  {r.url}")

    # --- MERCARI US (FAKE) ---
    # Simulated client for development
    print("\n--- Searching Mercari US (Simulated) ---")
    merc_us = MercariUSClient()
    mus_results = merc_us.search("jacket", limit=5)
    print(f"Found {len(mus_results)} simulated items on Mercari US:")

    for item in mus_results:
        print("-" * 20)
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"Link:  {item.url}")

    # --- DEPOP (FAKE) ---
    # Simulated client for development
    print("\n--- Searching Depop (Simulated) ---")
    depop = DepopClientFake()
    depop_results = depop.search("jacket", limit=5)
    print(f"Found {len(depop_results)} simulated items on Depop:")
    
    for item in depop_results:
        print("-" * 20)
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"Link:  {item.url}")

    # --- POSHMARK (FAKE) ---
    # Simulated client for development
    print("\n--- Searching Poshmark (Simulated) ---")
    posh = PoshmarkClientFake()
    posh_results = posh.search("jacket", limit=5)
    print(f"Found {len(posh_results)} simulated items on Poshmark:")
    
    for item in posh_results:
        print("-" * 20)
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"Link:  {item.url}")

    # --- FACEBOOK MARKETPLACE (FAKE BMWs) ---
    # Simulated client specifically tuned for cars/BMWs in this demo
    print("\n--- Searching Facebook Marketplace (Simulated BMW Data) ---")
    fb = FacebookMarketplaceClientFake()
    fb_results = fb.search("BMW", limit=20)
    print(f"Found {len(fb_results)} simulated BMW listings:")
    
    for item in fb_results:
        print("-" * 20)
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"Date:  {item.created_at}")
        print(f"Link:  {item.url}")

    print("\nDemo completed successfully.")


if __name__ == "__main__":
    main()
