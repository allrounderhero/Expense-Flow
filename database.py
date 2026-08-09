import psycopg2


def connect_db():

    con = psycopg2.connect(
        user="postgres",
        password="123654",
        host="127.0.0.1",
        port="5432",
        database="expense_records"
    )

    return con


def get_expenses():

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, title, exp_date, amount
        FROM expense
        ORDER BY id
    """)

    data = cur.fetchall()

    cur.close()
    con.close()

    return data


def add_expense(title, exp_date, amount):

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO expense (title, exp_date, amount)
        VALUES (%s, %s, %s)
    """, (title, exp_date, amount))

    con.commit()

    cur.close()
    con.close()


def update_expense(expense_id, title, exp_date, amount):

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        UPDATE expense
        SET title = %s,
            exp_date = %s,
            amount = %s
        WHERE id = %s
    """, (title, exp_date, amount, expense_id))

    con.commit()

    cur.close()
    con.close()


def delete_expense(expense_id):

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM expense WHERE id = %s",
        (expense_id,)
    )

    con.commit()

    cur.close()
    con.close()


def get_total_expense():

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expense"
    )

    total = cur.fetchone()[0]

    cur.close()
    con.close()

    return total


def get_transaction_count():

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM expense"
    )

    count = cur.fetchone()[0]

    cur.close()
    con.close()

    return count