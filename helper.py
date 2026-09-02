from datetime import datetime

from database import connect_db

expenses = []
expense_history = []


def normalize_date(value):
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value.isoformat()

    if isinstance(value, str):
        value = value.strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue

    raise ValueError(f"Unsupported date value: {value!r}")


def add_expense(title, exp_date, amount):
    exp_date = normalize_date(exp_date)

    con = connect_db()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO expense (title, exp_date, amount) VALUES (%s, %s, %s)",
        (title, exp_date, amount),
    )
    con.commit()
    cur.close()
    con.close()


def delete_expense(expense_id):
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM expense WHERE id = %s", (expense_id,))
    con.commit()
    cur.close()
    con.close()


def update_expense(expense_id, title, exp_date, amount):
    exp_date = normalize_date(exp_date)

    con = connect_db()
    cur = con.cursor()
    cur.execute(
        "UPDATE expense SET title = %s, exp_date = %s, amount = %s WHERE id = %s",
        (title, exp_date, amount, expense_id),
    )
    con.commit()
    cur.close()
    con.close()


def calculate_total():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expense")
    total = cur.fetchone()[0]
    cur.close()
    con.close()
    return total or 0


def get_transaction_count():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM expense")
    count = cur.fetchone()[0]
    cur.close()
    con.close()
    return count or 0


def get_today_expense(today_strs=None):
    con = connect_db()
    cur = con.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expense WHERE exp_date = CURRENT_DATE"
    )
    total = cur.fetchone()[0]
    cur.close()
    con.close()
    return total or 0


def get_category_breakdown():
    con = connect_db()
    cur = con.cursor()
    cur.execute(
        "SELECT title, COALESCE(SUM(amount), 0), COUNT(*) FROM expense GROUP BY title ORDER BY SUM(amount) DESC"
    )
    data = cur.fetchall()
    cur.close()
    con.close()
    return data


def get_expenses():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT id, title, exp_date, amount FROM expense ORDER BY id")
    data = cur.fetchall()
    cur.close()
    con.close()
    return data


def get_total_expense():
    return calculate_total()

