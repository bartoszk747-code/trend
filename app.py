from collections import defaultdict
from statistics import mean
from typing import List

from flask import Flask, render_template, request

from trend.api_clients.grailed_client import GrailedClient
from trend.api_clients.mercari_us_client import MercariUSClient
from trend.api_clients.depop_client_fake import DepopClientFake
from trend.api_clients.poshmark_client_fake import PoshmarkClientFake
from trend.api_clients.facebook_marketplace_client_fake import FacebookMarketplaceClientFake
from trend.db import init_db
from trend.models import Listing

print(">>> importing app.py")
app = Flask(__name__)

# Initialize DB and clients once
init_db()
grailed_client = GrailedClient()
mercari_us_client = MercariUSClient()
depop_client = DepopClientFake()
poshmark_client = PoshmarkClientFake()
facebook_client = FacebookMarketplaceClientFake()


def run_search(query: str, selected_sites: List[str], limit: int = 20) -> List[Listing]:
    all_results: List[Listing] = []

    if "grailed" in selected_sites:
        all_results.extend(grailed_client.search(query, limit=limit))

    if "mercari_us" in selected_sites:
        all_results.extend(mercari_us_client.search(query, limit=limit))

    if "depop" in selected_sites:
        all_results.extend(depop_client.search(query, limit=limit))

    if "poshmark" in selected_sites:
        all_results.extend(poshmark_client.search(query, limit=limit))

    if "facebook_marketplace" in selected_sites:
        # For BMW demos, query might be "BMW"
        all_results.extend(facebook_client.search(query, limit=limit))

    return all_results


def compute_stats(listings: List[Listing]):
    if not listings:
        return {
            "total": 0,
            "by_site": {},
            "avg_price_overall": None,
            "cheapest": None,
        }

    by_site_counts = defaultdict(int)
    by_site_prices = defaultdict(list)
    for l in listings:
        by_site_counts[l.site] += 1
        if l.price and l.price > 0:
            by_site_prices[l.site].append(l.price)

    by_site_avg = {
        site: round(mean(prices), 2) for site, prices in by_site_prices.items() if prices
    }

    # Cheapest listing overall
    valid = [l for l in listings if l.price is not None]
    cheapest = min(valid, key=lambda x: x.price) if valid else None

    # Overall average (all prices)
    all_prices = [l.price for l in valid if l.price and l.price > 0]
    avg_overall = round(mean(all_prices), 2) if all_prices else None

    return {
        "total": len(listings),
        "by_site": dict(by_site_counts),
        "avg_price_overall": avg_overall,
        "avg_price_by_site": by_site_avg,
        "cheapest": cheapest,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    selected_sites = ["grailed", "mercari_us", "depop", "poshmark", "facebook_marketplace"]
    results: List[Listing] = []
    stats = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        selected_sites = request.form.getlist("sites")

        if query and selected_sites:
            results = run_search(query, selected_sites, limit=20)
            stats = compute_stats(results)

    # Group results by site for nicer display
    grouped = defaultdict(list)
    for r in results:
        grouped[r.site].append(r)

    return render_template(
        "index.html",
        query=query,
        selected_sites=selected_sites,
        grouped_results=grouped,
        stats=stats,
    )


if __name__ == "__main__":
    print(">>> app.py started, starting Flask server...")
    app.run(debug=True)
