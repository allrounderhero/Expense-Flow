import os

from helper import expenses


def save_expense():

    fp = open("expense_details", "w")

    for item in expenses:
        line = item[0] + "#" + item[1] + "#" + item[2] + "#" + item[3] + "\n"
        fp.write(line)

    fp.close()


def load_expense():

    if not os.path.exists("expense_details"):
        fp = open("expense_details", "w")
        fp.close()
        return

    expenses.clear()

    fp = open("expense_details", "r")

    for line in fp:

        if not line.strip():
            continue

        data = line.strip().split("#")

        expenses.append(
            (data[0], data[1], data[2], data[3])
        )

    fp.close()
