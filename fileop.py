def save_expense(expenses):
    fp = open("expense_details", "w")

    for item in expenses:
        fp.write(item[0] + "#" + item[1] + "#" + item[2] + "\n")

    fp.close()


def load_expense():
    expenses = []

    try:
        fp = open("expense_details", "r")

        for line in fp:
            line = line.strip()
            if line:
                data = line.split("#")
                expenses.append((data[0], data[1], data[2]))

        fp.close()
    except FileNotFoundError:
        
        pass

    return expenses
