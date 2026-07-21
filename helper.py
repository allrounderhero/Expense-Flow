expenses = []
expense_history = []


def add_expense(category, amount, date):
    expenses.append((category, amount, date, "ACTIVE"))
    expense_history.append((category, amount, date, "ACTIVE"))


def delete_expense(index):
    item = expenses[index]
    expenses[index] = (item[0], item[1], item[2], "DELETED")
    expense_history.append((item[0], item[1], item[2], "DELETED"))


def update_expense(index, category, amount, date):
    old = expenses[index]
    expenses[index] = (old[0], old[1], old[2], "UPDATED")
    expense_history.append((old[0], old[1], old[2], "UPDATED"))

    expenses.append((category, amount, date, "ACTIVE"))
    expense_history.append((category, amount, date, "ACTIVE"))


def calculate_total():
    total = 0

    for item in expenses:
        if item[3] == "ACTIVE":
            total += int(item[1])

    return total


def get_transaction_count():
    count = 0

    for item in expenses:
        if item[3] == "ACTIVE":
            count += 1

    return count


def get_today_expense(today_strs):
    total = 0

    for item in expenses:
        if item[3] == "ACTIVE" and item[2] in today_strs:
            total += int(item[1])

    return total


def get_expenses():
    return expenses
