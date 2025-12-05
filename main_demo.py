from trend.api_clients.grailed_client import GrailedClient
from trend.api_clients.mercari_us_client import MercariUSClient
from trend.api_clients.depop_client_fake import DepopClientFake
from trend.api_clients.poshmark_client_fake import PoshmarkClientFake
from trend.api_clients.facebook_marketplace_client_fake import FacebookMarketplaceClientFake
from trend.db import init_db

def main():
    print("Running script...")
   #Cheks the DB exists, created tbls
    init_db()
    #grailed(real)
    client = GrailedClient()
    print("Searching Grailed...")
    results = client.search("jacket", limit=3)


    print(f"Grailed results found: {len(results)}")
    for r in results:
        print("----------")
        print("Site: Grailed")
        print("Title:", r.title)
        print("Price:", r.price, r.currency)
        print("URL:", r.url)

    #Mercari simulated
    print("\n--- Mercari US (FAKE) ---")
    merc_us = MercariUSClient()
    mus_results = merc_us.search("jacket", limit=5)
    print(f"Mercari US results found: {len(mus_results)}")


    for item in mus_results:
        print("----------")
        print("Site: Mercari US (simulated)")
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"URL: {item.url}")
        #DEPOP(simulated)
    print("\n--- Depop (FAKE) ---")
    depop = DepopClientFake()
    depop_results = depop.search("jacket", limit=5)
    print(f"Depop results found: {len(depop_results)}")
    for item in depop_results:
        print("----------")
        print("Site: Depop (simulated)")
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"URL: {item.url}")
    #Poshmark simulated
    print("\n--- Poshmark (FAKE) ---")
    posh = PoshmarkClientFake()
    posh_results = posh.search("jacket", limit=5)
    print(f"Poshmark results found: {len(posh_results)}")
    for item in posh_results:
        print("----------")
        print("Site: Poshmark (simulated)")
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"URL: {item.url}")
    #Facbook Marktpalce(Simulated BMW listings) Variable listings like on real marketplace
    print("\n--- Facebook Marketplace (FAKE BMW DATA) ---")
    fb = FacebookMarketplaceClientFake()
    fb_results = fb.search("BMW", limit=20)
    print(f"Facebook BMW results found: {len(fb_results)}")
    for item in fb_results:
        print("----------")
        print("Site: Facebook Marketplace (simulated)")
        print(f"Title: {item.title}")
        print(f"Price: {item.price} {item.currency}")
        print(f"URL: {item.url}")
        print(f"Date: {item.created_at}")


if __name__ == "__main__":
    #Tst script
    main()
