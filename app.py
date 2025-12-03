"""
Main Flask application for the Trend aggregator.
Handles routing, search logic aggregation, and basic statistics calculation.
"""

from collections import defaultdict
from statistics import mean
from typing import List

from flask import Flask, render_template, request

# Import our marketplace clients
from trend.api_clients.grailed_client import GrailedClient
from trend.api_clients.mercari_us_client import MercariUSClient
from trend.api_clients.depop_client_fake import DepopClientFake
from trend.api_clients.poshmark_client_fake import PoshmarkClientFake
from trend.api_clients.facebook_marketplace_client_fake import FacebookMarketplaceClientFake
from trend.db import init_db
from trend.models import Listing

print(">>> Initializing app.py...")
app = Flask(__name__)

# Initialize Database and API clients globally so we don't recreate them on every request
init_db()

# Instantiate clients
grailed_client = GrailedClient()
mercari_us_client = MercariUSClient()
depop_client = DepopClientFake()
poshmark_client = PoshmarkClientFake()
facebook_client = FacebookMarketplaceClientFake()


def run_search(query: str, selected_sites: List[str], category: str | None = None, limit: int = 20) -> List[Listing]:
    """
    Aggregates search results from all selected marketplace clients.
    
    Args:
        query: The search term.
        selected_sites: List of site names to include in the search.
        category: Optional category filter.
        limit: Max results per site.
        
    Returns:
        A combined list of Listing objects from all sources.
    """
    all_results: List[Listing] = []

    # Check each site and fetch results if selected
    if "grailed" in selected_sites:
        try:
            all_results.extend(grailed_client.search(query, category=category, limit=limit))
        except Exception as e:
            print(f"Error searching Grailed: {e}")

    if "mercari_us" in selected_sites:
        all_results.extend(mercari_us_client.search(query, category=category, limit=limit))

    if "depop" in selected_sites:
        all_results.extend(depop_client.search(query, category=category, limit=limit))

    if "poshmark" in selected_sites:
        all_results.extend(poshmark_client.search(query, category=category, limit=limit))

    if "facebook_marketplace" in selected_sites:
        # Note: Facebook client is currently simulated with BMW data for demo purposes
        all_results.extend(facebook_client.search(query, category=category, limit=limit))

    return all_results


def compute_stats(listings: List[Listing]) -> dict:
    """
    Calculates basic statistics from the search results.
    Includes total count, counts by site, average prices, and the cheapest item.
    """
    if not listings:
        return {
            "total": 0,
            "by_site": {},
            "avg_price_overall": None,
            "cheapest": None,
        }

    # Track counts and prices per site
    by_site_counts = defaultdict(int)
    by_site_prices = defaultdict(list)
    
    for l in listings:
        by_site_counts[l.site] += 1
        # Only consider valid prices for averages
        if l.price and l.price > 0:
            by_site_prices[l.site].append(l.price)

    # Calculate average price per site
    by_site_avg = {
        site: round(mean(prices), 2) for site, prices in by_site_prices.items() if prices
    }

    # Find the cheapest listing overall
    valid_listings = [l for l in listings if l.price is not None]
    cheapest = min(valid_listings, key=lambda x: x.price) if valid_listings else None

    # Calculate overall average price across all sites
    all_prices = [l.price for l in valid_listings if l.price and l.price > 0]
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
    """
    Home page route.
    Handles the search form submission and displays results.
    """
    # Default values
    query = ""
    category = ""
    # By default, select all available sites
    selected_sites = ["grailed", "mercari_us", "depop", "poshmark", "facebook_marketplace"]
    results: List[Listing] = []
    stats = None

    if request.method == "POST":
        # Get form data
        query = request.form.get("query", "").strip()
        category = request.form.get("category", "")
        selected_sites = request.form.getlist("sites")

        # Only search if we have a query and at least one site selected
        if query and selected_sites:
            print(f"Searching for '{query}' in '{category}' on {selected_sites}...")
            results = run_search(query, selected_sites, category=category if category else None, limit=20)
            stats = compute_stats(results)

    # Group results by site for easier rendering in the template
    grouped_results = defaultdict(list)
    for r in results:
        grouped_results[r.site].append(r)

    return render_template(
        "index.html",
        query=query,
        category=category,
        selected_sites=selected_sites,
        grouped_results=grouped_results,
        stats=stats,
    )


if __name__ == "__main__":
    print(">>> Starting Flask server in debug mode...")
    app.run(debug=True)
