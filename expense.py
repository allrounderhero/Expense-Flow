from helper import add_expense, display_expense, delete_expense, update_expense, total_expense
from fileop import save_expense, load_expense


def show_menu():
    print("------MENU------")
    print("1 -> Add Expense")
    print("2 -> Display Expenses")
    print("3 -> Delete Expense")
    print("4 -> Update Expense")
    print("5 -> Total Expense")
    print("0 -> Exit")


def main():
    expenses = load_expense()

    while True:
        show_menu()
        choice = input("Enter Your Choice : ")

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            display_expense(expenses)
        elif choice == "3":
            delete_expense(expenses)
        elif choice == "4":
            update_expense(expenses)
        elif choice == "5":
            total_expense(expenses)
        elif choice == "0":
            save_expense(expenses)
            print("Data Saved. Goodbye!")
            break
        else:
            print("Invalid Choice! Try Again.\n")


if __name__ == "__main__":
    main()
