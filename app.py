# Main application entry point
# Handles routing, search logic, and basic user session stuff (mocked for now)

from collections import defaultdict
from statistics import mean
from typing import List

from flask import Flask, render_template, request, abort, redirect, url_for

# Import our API clients - some are real, some are fake/simulated
from trend.api_clients.grailed_client import GrailedClient
from trend.api_clients.mercari_us_client import MercariUSClient
from trend.api_clients.depop_client_fake import DepopClientFake
from trend.api_clients.poshmark_client_fake import PoshmarkClientFake
from trend.api_clients.facebook_marketplace_client_fake import FacebookMarketplaceClientFake

from trend.db import init_db
from trend.models import Listing

# tiny helper that hits the DB for a rough "market" average
# (make sure trend/price_stats.py exists – see below)
from trend.price_stats import average_price_for_query

print(">>> importing app.py")
app = Flask(__name__)

# -------------------------------------
# INITIALIZATION
# -------------------------------------

# Initialize DB and clients
init_db()
grailed_client = GrailedClient()
mercari_us_client = MercariUSClient()
depop_client = DepopClientFake()
poshmark_client = PoshmarkClientFake()
facebook_client = FacebookMarketplaceClientFake()

# In-memory storage for watch rules (TODO: move to DB later)
watch_rules: list[dict] = []
_next_watch_id = 1

# Mock user for demo purposes
current_user = {
    "username": "demo_user",
    "email": "demo@trendtracker.app",
    "plan": "Beta access",
}


# -------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------

def normalize_url(site: str, url: str | None) -> str | None:
    """
    Helper to make sure we always have a valid clickable link.
    Some APIs return relative paths.
    """
    if not url:
        return None

    if url.startswith("http"):
        return url

    site_domains = {
        "grailed": "https://www.grailed.com",
        "depop": "https://www.depop.com",
        "poshmark": "https://poshmark.com",
        "mercari_us": "https://www.mercari.com",
        "facebook_marketplace": "https://www.facebook.com",
    }

    base = site_domains.get(site, "")
    return base + url


def run_search(query: str, selected_sites: List[str], limit: int = 20) -> List[Listing]:
    """
    Aggregates results from all selected marketplaces.
    """
    all_results: List[Listing] = []

    # Check which sites the user wants to search
    if "grailed" in selected_sites:
        all_results.extend(grailed_client.search(query, limit=limit))
    if "mercari_us" in selected_sites:
        all_results.extend(mercari_us_client.search(query, limit=limit))
    if "depop" in selected_sites:
        all_results.extend(depop_client.search(query, limit=limit))
    if "poshmark" in selected_sites:
        all_results.extend(poshmark_client.search(query, limit=limit))
    if "facebook_marketplace" in selected_sites:
        all_results.extend(facebook_client.search(query, limit=limit))

    # Fix up URLs before returning
    for r in all_results:
        r.url = normalize_url(r.site, getattr(r, "url", None))

    return all_results


def apply_filters(listings, tags=None, max_price=None):
    """
    Filters raw results based on user criteria.
    - tags: simple keyword matching (OR logic)
    - max_price: strict upper bound
    """
    if not listings:
        return []

    # clean up tags
    tags = [t.lower().strip() for t in (tags or []) if t.strip()]
    filtered = []

    for l in listings:
        # Combine all text fields for easier searching
        parts = [
            getattr(l, "title", "") or "",
            getattr(l, "brand", "") or "",
            getattr(l, "size", "") or "",
        ]
        text_raw = " ".join(parts).lower()

        # Normalize text to handle weird spacing/punctuation
        text = "".join(ch for ch in text_raw if ch.isalnum() or ch.isspace())
        text_no_space = text.replace(" ", "")

        # Check tags (if any)
        if tags:
            match_any = False
            for tag in tags:
                t = "".join(ch for ch in tag.lower() if ch.isalnum())
                if not t:
                    continue
                # check both with and without spaces to be safe
                if t in text or t in text_no_space:
                    match_any = True
                    break
            if not match_any:
                continue

        # Check price
        if max_price is not None and (l.price is None or l.price > max_price):
            continue

        filtered.append(l)

    return filtered


def compute_stats(listings: List[Listing]):
    """
    Calculates basic stats for the dashboard/analytics view.
    """
    if not listings:
        return {
            "total": 0,
            "by_site": {},
            "avg_price_overall": None,
            "avg_price_by_site": {},
            "cheapest": None,
        }

    by_site_counts = defaultdict(int)
    by_site_prices = defaultdict(list)

    for l in listings:
        by_site_counts[l.site] += 1
        if l.price and l.price > 0:
            by_site_prices[l.site].append(l.price)

    # Calculate averages per site
    by_site_avg = {
        site: round(mean(prices), 2)
        for site, prices in by_site_prices.items()
        if prices
    }

    valid = [l for l in listings if l.price is not None]
    cheapest = min(valid, key=lambda x: x.price) if valid else None

    all_prices = [l.price for l in valid if l.price and l.price > 0]
    avg_overall = round(mean(all_prices), 2) if all_prices else None

    return {
        "total": len(listings),
        "by_site": dict(by_site_counts),
        "avg_price_overall": avg_overall,
        "avg_price_by_site": by_site_avg,
        "cheapest": cheapest,
    }


def get_rule_matches(rule: dict) -> list[Listing]:
    # Helper to run a saved search rule
    raw = run_search(rule["query"], rule["sites"], limit=100)
    return apply_filters(raw, tags=rule["tags"], max_price=rule["max_price"])


# -------------------------------------
# ROUTES
# -------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    # Default values
    query = ""
    tags_input = ""
    max_price_input = ""
    selected_sites = ["grailed", "mercari_us", "depop", "poshmark", "facebook_marketplace"]
    results: List[Listing] = []
    stats = None

    if request.method == "POST":
        # Get form data
        query = request.form.get("query", "").strip()
        tags_input = request.form.get("tags", "").strip()
        max_price_input = request.form.get("max_price", "").strip()
        selected_sites = request.form.getlist("sites") or selected_sites

        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        max_price = None
        if max_price_input:
            try:
                max_price = float(max_price_input)
            except ValueError:
                # ignore invalid price input
                max_price = None

        if query and selected_sites:
            # Run the search!
            raw_results = run_search(query, selected_sites, limit=50)
            results = apply_filters(raw_results, tags=tags, max_price=max_price)
            stats = compute_stats(results)

    # Group results by site for display
    grouped = defaultdict(list)
    for r in results:
        grouped[r.site].append(r)

    return render_template(
        "index.html",
        query=query,
        tags_input=tags_input,
        max_price_input=max_price_input,
        selected_sites=selected_sites,
        grouped_results=grouped,
        stats=stats,
    )


@app.route("/watch", methods=["GET", "POST"])
def watch():
    global _next_watch_id

    message = None

    # Handle new watch rule creation
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        tags_input = request.form.get("tags", "").strip()
        max_price_input = request.form.get("max_price", "").strip()
        selected_sites = request.form.getlist("sites")

        tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()]

        max_price = None
        if max_price_input:
            try:
                max_price = float(max_price_input)
            except ValueError:
                max_price = None

        if query and selected_sites:
            watch_rules.append(
                {
                    "id": _next_watch_id,
                    "query": query,
                    "tags": tags,
                    "max_price": max_price,
                    "sites": selected_sites,
                    "seen_ids": set(),  # track what we've already notified about
                }
            )
            _next_watch_id += 1
            message = "Watch rule added!"
        else:
            message = "Please provide a query and at least one site."

    # Check for updates on existing rules
    notifications = []
    rule_summaries = []

    for rule in watch_rules:
        matches = get_rule_matches(rule)
        summary = compute_stats(matches)

        new_items = []
        for item in matches:
            if item.listing_id and item.listing_id not in rule["seen_ids"]:
                new_items.append(item)
                rule["seen_ids"].add(item.listing_id)

        if new_items:
            notifications.append({"rule": rule, "items": new_items})

        rule_summaries.append({"rule": rule, "summary": summary})

    return render_template(
        "watch.html",
        watch_rules=watch_rules,
        rule_summaries=rule_summaries,
        notifications=notifications,
        message=message,
    )


@app.route("/watch/<int:rule_id>")
def watch_detail(rule_id: int):
    # Find the rule
    rule = next((r for r in watch_rules if r["id"] == rule_id), None)
    if not rule:
        abort(404)

    # Get fresh results
    matches = get_rule_matches(rule)
    stats = compute_stats(matches)

    # Sort by price (cheapest first)
    matches_sorted = sorted(
        matches,
        key=lambda x: (x.price if x.price is not None else 1e9)
    )

    return render_template(
        "watch_detail.html",
        rule=rule,
        matches=matches_sorted,
        stats=stats,
    )


@app.route("/watch/<int:rule_id>/edit", methods=["GET", "POST"])
def watch_edit(rule_id: int):
    rule = next((r for r in watch_rules if r["id"] == rule_id), None)
    if not rule:
        abort(404)

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        tags_input = request.form.get("tags", "").strip()
        max_price_input = request.form.get("max_price", "").strip()
        selected_sites = request.form.getlist("sites")

        tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()]

        max_price = None
        if max_price_input:
            try:
                max_price = float(max_price_input)
            except ValueError:
                max_price = None

        # Update rule in place
        if query:
            rule["query"] = query
        rule["tags"] = tags
        rule["max_price"] = max_price
        if selected_sites:
            rule["sites"] = selected_sites

        return redirect(url_for("watch_detail", rule_id=rule_id))

    all_sites = [
        ("grailed", "Grailed"),
        ("mercari_us", "Mercari US (simulated)"),
        ("depop", "Depop (simulated)"),
        ("poshmark", "Poshmark (simulated)"),
        ("facebook_marketplace", "Facebook Marketplace (simulated)"),
    ]
    tags_string = ", ".join(rule.get("tags", [])) if rule.get("tags") else ""

    return render_template(
        "watch_edit.html",
        rule=rule,
        all_sites=all_sites,
        tags_string=tags_string,
    )


@app.route("/watch_add", methods=["POST"])
def watch_add():
    # Quick add from the search results page
    global _next_watch_id

    item = request.form.to_dict()
    title = (item.get("title") or "").strip()
    site = (item.get("site") or "").strip()
    price_raw = item.get("price")

    max_price = None
    if price_raw not in (None, ""):
        try:
            max_price = float(price_raw)
        except ValueError:
            max_price = None

    sites = [site] if site else []

    rule = {
        "id": _next_watch_id,
        "query": title or "Untitled watch",
        "tags": [],
        "max_price": max_price,
        "sites": sites,
        "seen_ids": set(),
    }
    watch_rules.append(rule)
    _next_watch_id += 1

    print("Added watch rule from listing:", rule)
    return redirect(url_for("watch_edit", rule_id=rule["id"]))


@app.route("/analytics")
def analytics():
    """
    New analytics endpoint:
      - One accordion card per watch rule
      - For each rule: stats, lowest price, DB historical avg
      - Trend data with: line+dots for “main” listing, dots for everything else (BaT style)
    """

    rule_blocks = []   # this becomes `rules` in analytics.html

    for rule in watch_rules:
        # always pull fresh matches so analytics feels "live"
        matches = get_rule_matches(rule)
        stats = compute_stats(matches)

        # cheapest from the stats helper
        lowest_listing = stats.get("cheapest")
        lowest_price = lowest_listing.price if lowest_listing else None
        lowest_currency = lowest_listing.currency if lowest_listing else None

        # optional "market" average from the DB
        try:
            historical_avg = average_price_for_query(rule["query"])
        except Exception as e:
            print("average_price_for_query failed:", e)
            historical_avg = None

        # only entries that actually have a datetime and a price
        dated = [m for m in matches if m.created_at and m.price]

        # sort by date so the charts don't jump around
        dated_sorted = sorted(dated, key=lambda m: m.created_at.isoformat())

        # treat the original query text as the "main" listing's title
        q_norm = (rule["query"] or "").strip().lower()

        def is_main_listing(listing):
            title_norm = (listing.title or "").strip().lower()
            return title_norm == q_norm

        # build chart points
        trend_points = []
        for m in dated_sorted:
            trend_points.append({
                "title": m.title,
                "date": m.created_at.isoformat(),
                "price": m.price,
                "site": m.site,
                "is_main": bool(is_main_listing(m)),
            })

        # average change per week for the main listing, if we have at least 2 data points
        avg_change_per_week = None
        main_points = [m for m in dated_sorted if is_main_listing(m)]

        if len(main_points) >= 2:
            first = main_points[0]
            last = main_points[-1]
            days = (last.created_at - first.created_at).days
            if days != 0:
                weeks = days / 7.0
                if weeks > 0:
                    change = last.price - first.price
                    avg_change_per_week = round(change / weeks, 2)

        # pack everything into one dict per rule
        rule_blocks.append({
            "id": rule["id"],
            "query": rule["query"],
            "sites": rule.get("sites", []),
            "tags": rule.get("tags", []),
            "stats": stats,
            "lowest_price": lowest_price,
            "lowest_currency": lowest_currency,
            "historical_avg": historical_avg,
            "avg_change_per_week": avg_change_per_week,
            "trend_points": trend_points,
        })

    return render_template("analytics.html", rules=rule_blocks)


@app.route("/profile")
def profile():
    total_rules = len(watch_rules)
    total_seen = sum(len(r["seen_ids"]) for r in watch_rules)

    return render_template(
        "profile.html",
        user=current_user,
        total_rules=total_rules,
        total_seen=total_seen,
    )


if __name__ == "__main__":
    print(">>> app.py started, starting Flask server...")
    app.run(debug=True)
