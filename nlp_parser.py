import re
from typing import Dict, List, Optional, Tuple

from db_config import university_db, sales_db


def execute_query(db, query: str, params: Optional[Tuple] = None) -> List[Dict]:
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()


DEPARTMENT_SYNONYMS: Dict[str, str] = {
    "cse": "CSE",
    "computer science": "CSE",
    "ece": "ECE",
    "electronics": "ECE",
    "mech": "MECH",
    "mechanical": "MECH",
}

PRODUCT_KEYWORDS = [
    "laptop",
    "phone",
    "mobile",
    "tablet",
    "headphone",
    "headphones",
    "camera",
    "monitor",
    "keyboard",
    "mouse",
    "printer",
]


def find_department(question: str) -> Optional[str]:
    for synonym, canonical in DEPARTMENT_SYNONYMS.items():
        if synonym in question:
            return canonical
    return None


def find_year(question: str) -> Optional[int]:
    # Matches: "year 2", "2nd year", "year: 3"
    match = re.search(r"\b(?:(?:year\s*:?)\s*(\d{1,2})|(\d{1,2})(?:st|nd|rd|th)?\s+year)\b", question)
    if match:
        num = match.group(1) or match.group(2)
        try:
            return int(num)
        except (TypeError, ValueError):
            return None
    return None


def find_limit(question: str) -> Optional[int]:
    match = re.search(r"\b(?:top|first|limit)\s+(\d{1,3})\b", question)
    if match:
        try:
            value = int(match.group(1))
            return value if value > 0 else None
        except ValueError:
            return None
    return None


def find_product(question: str) -> Optional[str]:
    for word in PRODUCT_KEYWORDS:
        if word in question:
            # Capitalize first letter like example dataset (e.g., "Laptop")
            return word.capitalize()
    return None


def parse_question(question: str):
    q = (question or "").lower().strip()

    # ----------------- Cross-database queries -----------------
    if re.search(r"\b(department\s+sales|sales\s+by\s+department|department-?wise\s+sales|sales\s+per\s+department)\b", q):
        query = (
            """
            SELECT s.department, SUM(t.amount) AS total_sales
            FROM University.students s
            JOIN Sales.transactions t
                ON s.name = t.customer
            GROUP BY s.department
            ORDER BY total_sales DESC
            """
        )
        return execute_query(university_db, query)

    if re.search(r"\b(students?\s+with\s+sales|student\s+sales\s+totals|students?\s+and\s+sales|sales\s+per\s+student)\b", q):
        query = (
            """
            SELECT s.name, s.department, s.year, COALESCE(SUM(t.amount), 0) AS total_sales
            FROM University.students s
            LEFT JOIN Sales.transactions t
                ON s.name = t.customer
            GROUP BY s.name, s.department, s.year
            ORDER BY total_sales DESC
            """
        )
        return execute_query(university_db, query)

    if re.search(r"\b(highest|max|top)\s+(transaction|sale)s?\b", q):
        query = (
            """
            SELECT t.customer, t.product, t.amount
            FROM Sales.transactions t
            WHERE t.amount = (SELECT MAX(amount) FROM Sales.transactions)
            """
        )
        return execute_query(sales_db, query)

    # ----------------- University queries -----------------
    if "student" in q:
        conditions = []
        params: List = []

        dept = find_department(q)
        if dept:
            conditions.append("department = %s")
            params.append(dept)

        year = find_year(q)
        if year is not None:
            conditions.append("year = %s")
            params.append(year)

        where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        limit = find_limit(q) or 20

        query = f"SELECT id, name, department, year FROM students{where_clause} ORDER BY id ASC LIMIT %s"
        params.append(limit)
        return execute_query(university_db, query, tuple(params))

    # ----------------- Sales queries -----------------
    # List of distinct products
    if re.search(r"\b(all\s+products|products?\s+(available|list|names?)|list\s+products?)\b", q) or q.strip() in {"products", "product list"}:
        limit = find_limit(q)
        base = "SELECT DISTINCT product FROM transactions ORDER BY product ASC"
        if limit:
            return execute_query(sales_db, base + " LIMIT %s", (limit,))
        return execute_query(sales_db, base)

    # Product sales in ascending order
    if re.search(r"\b(product\s+sales?\s+(asc|ascending)|sales?\s+by\s+product\s+(asc|ascending)|ascending\s+product\s+sales?)\b", q):
        limit = find_limit(q)
        base = "SELECT id, customer, product, amount FROM transactions ORDER BY amount ASC"
        if limit:
            return execute_query(sales_db, base + " LIMIT %s", (limit,))
        return execute_query(sales_db, base)

    if "transaction" in q or "sale" in q:
        conditions = []
        params: List = []

        product = find_product(q)
        if product:
            conditions.append("product = %s")
            params.append(product)

        where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        limit = find_limit(q) or 20

        query = f"SELECT id, customer, product, amount FROM transactions{where_clause} ORDER BY id DESC LIMIT %s"
        params.append(limit)
        return execute_query(sales_db, query, tuple(params))

    # ----------------- Fallback -----------------
    return [{"error": "I could not understand the question."}]
