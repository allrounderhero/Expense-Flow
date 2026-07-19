def add_expense(expenses):
    category = input("Enter Category : ")
    amount = input("Enter Amount : ")
    date = input("Enter Date : ")

    expenses.append((category, amount, date))
    print("Expense Added Successfully!\n")


def display_expense(expenses):
    if not expenses:
        print("No Expenses Found!\n")
        return

    print("\nID  CATEGORY        AMOUNT      DATE")
    print("-" * 40)
    for id, item in enumerate(expenses):
        print(f"{id:<3} {item[0]:<15} {item[1]:<11} {item[2]}")
    print()


def delete_expense(expenses):
    display_expense(expenses)

    if not expenses:
        return

    id = int(input("Enter ID to Delete : "))

    if 0 <= id < len(expenses):
        del expenses[id]
        print("Expense Deleted Successfully!\n")
    else:
        print("Invalid ID!\n")


def update_expense(expenses):
    display_expense(expenses)

    if not expenses:
        return

    id = int(input("Enter ID to Update : "))

    if 0 <= id < len(expenses):
        category = input("Enter Category : ")
        amount = input("Enter Amount : ")
        date = input("Enter Date : ")

        expenses[id] = (category, amount, date)
        print("Expense Updated Successfully!\n")
    else:
        print("Invalid ID!\n")


def total_expense(expenses):
    total = 0

    for item in expenses:
        total += int(item[1])

    print("Total Expense =", total, "\n")
