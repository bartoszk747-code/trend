from collections import defaultdict
from statistics import mean
from typing import List
from flask import Flask, render_template, request, abort, redirect

from trend.api_clients.grailed_client import GrailedClient
from trend.api_clients.mercari_us_client import MercariUSClient
from trend.api_clients.depop_client_fake import DepopClientFake
from trend.api_clients.poshmark_client_fake import PoshmarkClientFake
from trend.api_clients.facebook_marketplace_client_fake import FacebookMarketplaceClientFake

from trend.db import init_db
from trend.models import Listing

print(">>> importing app.py")
app = Flask(__name__)

# ---------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------

init_db()
grailed_client = GrailedClient()
mercari_us_client = MercariUSClient()
depop_client = DepopClientFake()
poshmark_client = PoshmarkClientFake()
facebook_client = FacebookMarketplaceClientFake()

watch_rules: list[dict] = []
analytics_items: list[dict] = []   # <-- NOW ADDED CORRECTLY
_next_watch_id = 1

current_user = {
    "username": "demo_user",
    "email": "demo@trendtracker.app",
    "plan": "Beta access",
}

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------

def normalize_url(site: str, url: str):
    if not url:
        return None

    if url.startswith("http"):
        return url

    domains = {
        "grailed": "https://www.grailed.com",
        "depop": "https://www.depop.com",
        "poshmark": "https://poshmark.com",
        "mercari_us": "https://www.mercari.com",
        "facebook_marketplace": "https://www.facebook.com",
    }

    return domains.get(site, "") + url


def run_search(query: str, selected_sites: List[str], limit: int = 20) -> List[Listing]:
    results = []

    if "grailed" in selected_sites:
        results.extend(grailed_client.search(query, limit=limit))

    if "mercari_us" in selected_sites:
        results.extend(mercari_us_client.search(query, limit=limit))

    if "depop" in selected_sites:
        results.extend(depop_client.search(query, limit=limit))

    if "poshmark" in selected_sites:
        results.extend(poshmark_client.search(query, limit=limit))

    if "facebook_marketplace" in selected_sites:
        results.extend(facebook_client.search(query, limit=limit))

    # Normalize URLs
    for r in results:
        r.url = normalize_url(r.site, r.url)

    return results


def apply_filters(listings, tags=None, max_price=None):
    if not listings:
        return []

    tags = [t.lower() for t in (tags or []) if t.strip()]
    filtered = []

    for l in listings:
        title = (l.title or "").lower()

        if tags and not all(tag in title for tag in tags):
            continue

        if max_price is not None and (l.price is None or l.price > max_price):
            continue

        filtered.append(l)

    return filtered


def compute_stats(listings: List[Listing]):
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


def get_rule_matches(rule):
    raw = run_search(rule["query"], rule["sites"], limit=100)
    return apply_filters(raw, tags=rule["tags"], max_price=rule["max_price"])


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    tags_input = ""
    max_price_input = ""
    selected_sites = ["grailed", "mercari_us", "depop", "poshmark", "facebook_marketplace"]
    results = []
    stats = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        tags_input = request.form.get("tags", "").strip()
        max_price_input = request.form.get("max_price", "").strip()
        selected_sites = request.form.getlist("sites")

        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        max_price = None
        if max_price_input:
            try:
                max_price = float(max_price_input)
            except:
                max_price = None

        raw_results = run_search(query, selected_sites, limit=50)
        results = apply_filters(raw_results, tags, max_price)
        stats = compute_stats(results)

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

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        tags_raw = request.form.get("tags", "").strip()
        max_price_raw = request.form.get("max_price", "").strip()
        sites = request.form.getlist("sites")

        tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]

        max_price = None
        if max_price_raw:
            try:
                max_price = float(max_price_raw)
            except:
                max_price = None

        if query and sites:
            watch_rules.append({
                "id": _next_watch_id,
                "query": query,
                "tags": tags,
                "max_price": max_price,
                "sites": sites,
                "seen_ids": set(),
            })
            _next_watch_id += 1
            message = "Watch rule added!"

    rule_summaries = []
    notifications = []

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
        rule_summaries=rule_summaries,
        notifications=notifications,
        message=message,
    )


@app.route("/watch/<int:rule_id>")
def watch_detail(rule_id):
    rule = next((r for r in watch_rules if r["id"] == rule_id), None)
    if not rule:
        abort(404)

    matches = get_rule_matches(rule)
    stats = compute_stats(matches)
    matches_sorted = sorted(matches, key=lambda x: (x.price if x.price else 1e9))

    return render_template(
        "watch_detail.html",
        rule=rule,
        matches=matches_sorted,
        stats=stats,
    )


# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

@app.route("/analytics")
def analytics():
    rule_labels = []
    rule_avg_prices = []
    rule_price_drops = []
    trend_points = []

    for rule in watch_rules:
        matches = get_rule_matches(rule)
        stats = compute_stats(matches)

        if stats["avg_price_overall"]:
            rule_labels.append(rule["query"])
            rule_avg_prices.append(stats["avg_price_overall"])

        dated = [m for m in matches if m.created_at and m.price]
        if len(dated) >= 2:
            sorted_dates = sorted(dated, key=lambda x: x.created_at)
            drop = sorted_dates[0].price - sorted_dates[-1].price
            rule_price_drops.append(round(drop, 2))
        else:
            rule_price_drops.append(0)

        for m in dated:
            trend_points.append({
                "rule": rule["query"],
                "title": m.title,
                "date": m.created_at.isoformat(),
                "price": m.price,
            })

    trend_points.sort(key=lambda x: x["date"])

    analytics_data = {
        "labels": rule_labels,
        "avg_prices": rule_avg_prices,
        "price_drops": rule_price_drops,
        "trend_points": trend_points,
        "saved_items": analytics_items,   # <-- NEW
    }

    return render_template("analytics.html", analytics_data=analytics_data)


# ---------------------------------------------------------
# PARTIAL SAVE ROUTES
# ---------------------------------------------------------

@app.route("/analytics_add", methods=["POST"])
def analytics_add():
    item = request.form.to_dict()
    item["url"] = normalize_url(item.get("site"), item.get("url"))
    analytics_items.append(item)
    print("Saved to analytics:", item)
    return redirect("/analytics")


@app.route("/watch_add", methods=["POST"])
def watch_add():
    item = request.form.to_dict()
    title = item.get("title", "")

    watch_rules.append({
        "id": len(watch_rules) + 1,
        "query": title,
        "tags": [],
        "max_price": None,
        "sites": [item.get("site")],
        "seen_ids": set(),
    })

    print("Added watch rule:", title)
    return redirect("/watch")


# ---------------------------------------------------------
# PROFILE
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    print(">>> app.py started, starting Flask server...")
    app.run(debug=True)
