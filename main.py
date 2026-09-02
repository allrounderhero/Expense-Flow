from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_expenses, add_expense, update_expense, delete_expense, get_total_expense

app = FastAPI(title="Expense Tracker API")


class Expense(BaseModel):
    category: str
    amount: int
    date: str


@app.get("/")
def read_root():
    return {"message": "Expense Tracker API is running"}


# CREATE
@app.post("/expenses/")
def create_expense(expense: Expense):

    add_expense(expense.category, expense.date, expense.amount)

    return {
        "message": "Expense added successfully",
        "expense": {
            "category": expense.category,
            "amount": expense.amount,
            "date": expense.date
        }
    }


# READ ALL
@app.get("/expenses/")
def get_all_expenses():

    expenses = get_expenses()

    result = []

    for item in expenses:
        result.append({
            "id": item[0],
            "category": item[1],
            "date": item[2],
            "amount": item[3]
        })

    return {
        "expenses": result
    }


# TOTAL
@app.get("/expenses/total")
def get_total():

    total = get_total_expense()

    return {
        "total_expense": total
    }


# READ ONE
@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):

    expenses = get_expenses()

    for item in expenses:
        if item[0] == expense_id:
            return {
                "id": item[0],
                "category": item[1],
                "date": item[2],
                "amount": item[3]
            }

    raise HTTPException(
        status_code=404,
        detail="Expense not found"
    )


# UPDATE
@app.put("/expenses/{expense_id}")
def update_single_expense(expense_id: int, expense: Expense):

    expenses = get_expenses()
    
    expense_found = False
    for item in expenses:
        if item[0] == expense_id:
            expense_found = True
            break

    if not expense_found:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    update_expense(expense_id, expense.category, expense.date, expense.amount)

    return {
        "message": "Expense updated successfully",
        "expense": {
            "id": expense_id,
            "category": expense.category,
            "amount": expense.amount,
            "date": expense.date
        }
    }


# DELETE
@app.delete("/expenses/{expense_id}")
def delete_single_expense(expense_id: int):

    expenses = get_expenses()

    expense_found = False
    deleted_expense = None
    for item in expenses:
        if item[0] == expense_id:
            expense_found = True
            deleted_expense = item
            break

    if not expense_found:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    delete_expense(expense_id)

    return {
        "message": "Expense deleted successfully",
        "deleted_expense": {
            "id": deleted_expense[0],
            "category": deleted_expense[1],
            "date": deleted_expense[2],
            "amount": deleted_expense[3]
        }
    }