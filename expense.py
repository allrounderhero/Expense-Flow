import tkinter as tk
from tkinter import ttk
from datetime import datetime

from helper import *
from fileop import *

load_expense()

# ===== Create Window =====
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("1000x700")
root.minsize(900, 650)
root.configure(bg="#f0f0f0")


# ===== Header Frame =====
header_frame = tk.Frame(root, bg="#2c3e50", height=60)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

tk.Label(
    header_frame,
    text="EXPENSE TRACKER",
    font=("Arial", 20, "bold"),
    bg="#2c3e50",
    fg="white"
).pack(expand=True)


# ===== Middle Frame (Quick Add + Summary) =====
middle_frame = tk.Frame(root, bg="#f0f0f0")
middle_frame.pack(fill=tk.X, padx=20, pady=10)


# --- Quick Add Expense ---
quick_add_frame = ttk.LabelFrame(
    middle_frame,
    text="  QUICK ADD EXPENSE  ",
    padding=15
)
quick_add_frame.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True,
    padx=(0, 10)
)

ttk.Label(
    quick_add_frame,
    text="Category :",
    font=("Arial", 10)
).grid(row=0, column=0, sticky="w", pady=8)

category_entry = ttk.Entry(quick_add_frame, width=25)
category_entry.grid(row=0, column=1, pady=8, padx=(10, 0))

ttk.Label(
    quick_add_frame,
    text="Amount :",
    font=("Arial", 10)
).grid(row=1, column=0, sticky="w", pady=8)

amount_entry = ttk.Entry(quick_add_frame, width=25)
amount_entry.grid(row=1, column=1, pady=8, padx=(10, 0))

ttk.Label(
    quick_add_frame,
    text="Date :",
    font=("Arial", 10)
).grid(row=2, column=0, sticky="w", pady=8)

date_entry = ttk.Entry(quick_add_frame, width=25)
date_entry.grid(row=2, column=1, pady=8, padx=(10, 0))


# --- Expense Summary ---
summary_frame = ttk.LabelFrame(
    middle_frame,
    text="  EXPENSE SUMMARY  ",
    padding=15
)
summary_frame.pack(
    side=tk.RIGHT,
    fill=tk.BOTH,
    expand=True,
    padx=(10, 0)
)

total_label = ttk.Label(
    summary_frame,
    text="Total Expense      : ₹0",
    font=("Arial", 12)
)
total_label.grid(row=0, column=0, sticky="w", pady=8)

transaction_label = ttk.Label(
    summary_frame,
    text="Total Transactions : 0",
    font=("Arial", 12)
)
transaction_label.grid(row=1, column=0, sticky="w", pady=8)

today_label = ttk.Label(
    summary_frame,
    text="Today's Expense    : ₹0",
    font=("Arial", 12)
)
today_label.grid(row=2, column=0, sticky="w", pady=8)


# ===== Expense List Frame =====
list_frame = ttk.LabelFrame(
    root,
    text="  EXPENSES  ",
    padding=10
)
list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

# Column Headings
heading_frame = tk.Frame(list_frame)
heading_frame.pack(fill=tk.X)

col_widths = [20, 15, 15, 25]
headings = ["Category", "Amount", "Date", "Actions"]

for i, head in enumerate(headings):

    tk.Label(
        heading_frame,
        text=head,
        font=("Arial", 12, "bold"),
        width=col_widths[i],
        anchor="w"
    ).pack(side=tk.LEFT, padx=5)

ttk.Separator(
    list_frame,
    orient="horizontal"
).pack(fill=tk.X, pady=5)

# Scrollable Area
canvas = tk.Canvas(list_frame, highlightthickness=0, bg="white")

scrollbar = ttk.Scrollbar(
    list_frame,
    orient="vertical",
    command=canvas.yview
)

expense_frame = tk.Frame(canvas, bg="white")

expense_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas_window = canvas.create_window(
    (0, 0),
    window=expense_frame,
    anchor="nw"
)


def on_canvas_configure(event):
    canvas.itemconfig(canvas_window, width=event.width)


canvas.bind("<Configure>", on_canvas_configure)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


# Mouse Wheel Scrolling
def on_mousewheel(event):
    canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))


# ===== History Button =====
history_btn_frame = tk.Frame(root, bg="#f0f0f0")
history_btn_frame.pack(fill=tk.X, padx=20, pady=5)


# ===== Status Bar =====
status_var = tk.StringVar(value="Status : Ready")

status_bar = tk.Label(
    root,
    textvariable=status_var,
    bd=1,
    relief=tk.SUNKEN,
    anchor=tk.W,
    font=("Arial", 9),
    padx=10,
    pady=5
)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)


# ===== Helper: Today's Date Strings =====
def get_today_strings():

    today = datetime.now()
    today_strs = set()

    today_strs.add(today.strftime("%d/%m/%Y"))
    today_strs.add(today.strftime("%d/%m/%y"))

    try:
        today_strs.add(today.strftime("%#d/%#m/%Y"))
        today_strs.add(today.strftime("%#d/%#m/%y"))
    except ValueError:
        pass

    return today_strs


# ===== Display Expenses =====
def display_expenses():

    for widget in expense_frame.winfo_children():
        widget.destroy()

    expenses_list = get_expenses()
    row_num = 0

    for i, item in enumerate(expenses_list):

        if item[3] != "ACTIVE":
            continue

        bg = "white" if row_num % 2 == 0 else "#f8f8f8"

        row = tk.Frame(expense_frame, bg=bg)
        row.pack(fill=tk.X, pady=1)

        tk.Label(
            row,
            text=item[0],
            font=("Arial", 10),
            width=20,
            anchor="w",
            bg=bg
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            row,
            text=f"₹{item[1]}",
            font=("Arial", 10),
            width=15,
            anchor="w",
            bg=bg
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            row,
            text=item[2],
            font=("Arial", 10),
            width=15,
            anchor="w",
            bg=bg
        ).pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(row, bg=bg)
        btn_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="✏ Edit",
            command=lambda x=i: edit_expense(x)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🗑 Delete",
            command=lambda x=i: delete_gui(x)
        ).pack(side=tk.LEFT, padx=5)

        row_num += 1


# ===== Update Summary =====
def update_summary():

    total = calculate_total()
    total_label.config(
        text=f"Total Expense      : ₹{total}"
    )

    count = get_transaction_count()
    transaction_label.config(
        text=f"Total Transactions : {count}"
    )

    today_strs = get_today_strings()
    today_total = get_today_expense(today_strs)
    today_label.config(
        text=f"Today's Expense    : ₹{today_total}"
    )


# ===== Refresh GUI =====
def refresh_gui():

    load_expense()

    display_expenses()

    update_summary()


# ===== Add Expense =====
def add_expense_gui():

    category = category_entry.get()
    amount = amount_entry.get()
    date = date_entry.get()

    if not category or not amount or not date:
        status_var.set("Status : Please fill all fields")
        return

    add_expense(category, amount, date)

    save_expense()

    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

    status_var.set("Status : Expense added successfully")

    refresh_gui()


# Add Button (inside quick_add_frame)
add_btn = ttk.Button(
    quick_add_frame,
    text="ADD EXPENSE",
    command=add_expense_gui
)
add_btn.grid(row=3, column=0, columnspan=2, pady=(15, 5))


# ===== Delete Expense =====
def delete_gui(index):

    delete_expense(index)

    save_expense()

    status_var.set("Status : Expense deleted")

    refresh_gui()


# ===== Edit Expense (Popup) =====
def edit_expense(index):

    item = get_expenses()[index]

    popup = tk.Toplevel(root)
    popup.title("Edit Expense")
    popup.geometry("380x280")
    popup.resizable(False, False)
    popup.grab_set()

    # Center the popup on the main window
    popup.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (380 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (280 // 2)
    popup.geometry(f"+{x}+{y}")

    tk.Label(
        popup,
        text="EDIT EXPENSE",
        font=("Arial", 14, "bold")
    ).pack(pady=(15, 10))

    form = tk.Frame(popup)
    form.pack(padx=30, pady=5)

    tk.Label(
        form,
        text="Category :",
        font=("Arial", 10)
    ).grid(row=0, column=0, sticky="w", pady=8)

    cat_entry = ttk.Entry(form, width=25)
    cat_entry.grid(row=0, column=1, pady=8, padx=(10, 0))
    cat_entry.insert(0, item[0])

    tk.Label(
        form,
        text="Amount :",
        font=("Arial", 10)
    ).grid(row=1, column=0, sticky="w", pady=8)

    amt_entry = ttk.Entry(form, width=25)
    amt_entry.grid(row=1, column=1, pady=8, padx=(10, 0))
    amt_entry.insert(0, item[1])

    tk.Label(
        form,
        text="Date :",
        font=("Arial", 10)
    ).grid(row=2, column=0, sticky="w", pady=8)


    dt_entry = ttk.Entry(form, width=25)
    dt_entry.grid(row=2, column=1, pady=8, padx=(10, 0))
    dt_entry.insert(0, item[2])

    def save_changes():

        category = cat_entry.get()
        amount = amt_entry.get()
        date = dt_entry.get()

        update_expense(index, category, amount, date)

        save_expense()

        popup.destroy()

        status_var.set("Status : Expense updated successfully")

        refresh_gui()

    ttk.Button(
        popup,
        text="SAVE CHANGES",
        command=save_changes
    ).pack(pady=15)


# ===== View Expense History (Popup) =====
def view_history():

    popup = tk.Toplevel(root)
    popup.title("Expense History")
    popup.geometry("700x500")
    popup.resizable(True, True)

    # Center the popup
    popup.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (700 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (500 // 2)
    popup.geometry(f"+{x}+{y}")

    tk.Label(
        popup,
        text="EXPENSE HISTORY",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    # Headings
    h_frame = tk.Frame(popup)
    h_frame.pack(fill=tk.X, padx=20)

    for head in ["Category", "Amount", "Date", "Status"]:

        tk.Label(
            h_frame,
            text=head,
            font=("Arial", 11, "bold"),
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)

    ttk.Separator(
        popup,
        orient="horizontal"
    ).pack(fill=tk.X, padx=20, pady=5)

    # Scrollable List
    h_canvas = tk.Canvas(popup, highlightthickness=0)

    h_scrollbar = ttk.Scrollbar(
        popup,
        orient="vertical",
        command=h_canvas.yview
    )

    h_frame_inner = tk.Frame(h_canvas)

    h_frame_inner.bind(
        "<Configure>",
        lambda e: h_canvas.configure(
            scrollregion=h_canvas.bbox("all")
        )
    )

    h_canvas.create_window(
        (0, 0),
        window=h_frame_inner,
        anchor="nw"
    )
    h_canvas.configure(yscrollcommand=h_scrollbar.set)

    h_canvas.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True,
        padx=(20, 0)
    )
    h_scrollbar.pack(
        side=tk.RIGHT,
        fill=tk.Y,
        padx=(0, 20)
    )

    # Mouse wheel for history popup
    def h_mousewheel(event):
        h_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    h_canvas.bind("<Enter>", lambda e: h_canvas.bind_all("<MouseWheel>", h_mousewheel))
    h_canvas.bind("<Leave>", lambda e: h_canvas.unbind_all("<MouseWheel>"))

    status_colors = {
        "ACTIVE": "#27ae60",
        "UPDATED": "#e67e22",
        "DELETED": "#e74c3c"
    }

    for item in get_expenses():

        row = tk.Frame(h_frame_inner)
        row.pack(fill=tk.X, pady=2)

        tk.Label(
            row,
            text=item[0],
            width=15,
            anchor="w",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            row,
            text=f"₹{item[1]}",
            width=15,
            anchor="w",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            row,
            text=item[2],
            width=15,
            anchor="w",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        color = status_colors.get(item[3], "black")

        tk.Label(
            row,
            text=item[3],
            width=15,
            anchor="w",
            font=("Arial", 10, "bold"),
            fg=color
        ).pack(side=tk.LEFT, padx=5)


# History Button
history_btn = ttk.Button(
    history_btn_frame,
    text="VIEW EXPENSE HISTORY",
    command=view_history
)
history_btn.pack()


# ===== Start GUI =====
refresh_gui()

root.mainloop()
