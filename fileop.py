import os

FILE_PATH = "expense_details"


def save_expense(expenses):
    with open(FILE_PATH, "w") as fp:
        for item in expenses:
            line = item[0] + "#" + item[1] + "#" + item[2] + "\n"
            fp.write(line)


def load_expense():
    if not os.path.exists(FILE_PATH):
        open(FILE_PATH, "w").close()
        return []

    expenses = []

    with open(FILE_PATH, "r") as fp:
        for line in fp:
            if not line.strip():
                continue
            data = line.strip().split("#")
            if len(data) == 3:
                expenses.append((data[0], data[1], data[2]))

    return expenses