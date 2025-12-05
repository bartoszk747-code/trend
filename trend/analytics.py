from .db import get_conn

def average_price_for_query(query: str):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT AVG(price) AS avg_price
        FROM listings
        WHERE title LIKE ?
    """, (f"%{query}%",))

    row = c.fetchone()
    conn.close()

    return row["avg_price"] if row and row["avg_price"] is not None else None