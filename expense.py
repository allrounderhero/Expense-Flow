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

# Color / font theme
BG_COLOR = "#f7f9fc"
CARD_BG = "#ffffff"
ACCENT = "#0a74da"
FONT_FAMILY = "Segoe UI"
FONT_LARGE = (FONT_FAMILY, 20, "bold")
FONT_HEADER = (FONT_FAMILY, 16, "bold")
FONT_MEDIUM = (FONT_FAMILY, 12)
FONT_HEADING_BOLD = (FONT_FAMILY, 12, "bold")
FONT_HISTORY_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_TINY = (FONT_FAMILY, 9)

root.configure(bg=BG_COLOR)

# ttk styling
style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

style.configure("TButton", font=FONT_SMALL, padding=6)
style.configure("TLabel", background=BG_COLOR, font=FONT_MEDIUM)
style.configure("Card.TLabelframe", background=BG_COLOR, borderwidth=0)
style.configure("Card.TLabelframe.Label", font=FONT_SMALL)
style.configure("Accent.TButton", foreground="white", background=ACCENT)
style.map("Accent.TButton",
            background=[('active', '#095bb5')])


# ===== Header Frame =====
header_frame = tk.Frame(root, bg=ACCENT, height=60)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

tk.Label(
    header_frame,
    text="EXPENSE TRACKER",
    font=FONT_LARGE,
    bg=ACCENT,
    fg="white"
).pack(expand=True)


# ===== Middle Frame (Quick Add + Summary) =====
middle_frame = tk.Frame(root, bg=BG_COLOR)
middle_frame.pack(fill=tk.X, padx=24, pady=14)


# --- Quick Add Expense ---
quick_add_frame = ttk.LabelFrame(
    middle_frame,
    text="  QUICK ADD EXPENSE  ",
    padding=16,
    style="Card.TLabelframe"
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
    font=FONT_SMALL
).grid(row=0, column=0, sticky="w", pady=8)

category_entry = ttk.Entry(quick_add_frame, width=28)
category_entry.grid(row=0, column=1, pady=8, padx=(10, 0))

ttk.Label(
    quick_add_frame,
    text="Amount :",
    font=FONT_SMALL
).grid(row=1, column=0, sticky="w", pady=8)

amount_entry = ttk.Entry(quick_add_frame, width=28)
amount_entry.grid(row=1, column=1, pady=8, padx=(10, 0))

ttk.Label(
    quick_add_frame,
    text="Date :",
    font=FONT_SMALL
).grid(row=2, column=0, sticky="w", pady=8)

date_entry = ttk.Entry(quick_add_frame, width=28)
date_entry.grid(row=2, column=1, pady=8, padx=(10, 0))


# --- Expense Summary ---
summary_frame = ttk.LabelFrame(
    middle_frame,
    text="  EXPENSE SUMMARY  ",
    padding=16,
    style="Card.TLabelframe"
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
    font=FONT_MEDIUM
)
total_label.grid(row=0, column=0, sticky="w", pady=8)

transaction_label = ttk.Label(
    summary_frame,
    text="Total Transactions : 0",
    font=FONT_MEDIUM
)
transaction_label.grid(row=1, column=0, sticky="w", pady=8)

today_label = ttk.Label(
    summary_frame,
    text="Today's Expense    : ₹0",
    font=FONT_MEDIUM
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
        font=FONT_HEADING_BOLD,
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
history_btn_frame = tk.Frame(root, bg=BG_COLOR)
history_btn_frame.pack(fill=tk.X, padx=20, pady=5)


# ===== Status Bar =====
status_var = tk.StringVar(value="Status : Ready")

status_bar = tk.Label(
    root,
    textvariable=status_var,
    bd=1,
    relief=tk.SUNKEN,
    anchor=tk.W,
    font=FONT_TINY,
    padx=10,
    pady=5,
    bg=CARD_BG
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

    for item in expenses_list:

        expense_id = item[0]
        category = item[1]
        date = item[2]
        amount = item[3]

        bg = "white" if row_num % 2 == 0 else "#f8f8f8"

        row = tk.Frame(
            expense_frame,
            bg=bg
        )

        row.pack(
            fill=tk.X,
            pady=1
        )

        # Category
        tk.Label(
            row,
            text=category,
            font=FONT_SMALL,
            width=20,
            anchor="w",
            bg=bg
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # Amount
        tk.Label(
            row,
            text=f"₹{amount:.2f}",
            font=FONT_SMALL,
            width=15,
            anchor="w",
            bg=bg
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # Date
        tk.Label(
            row,
            text=str(date),
            font=FONT_SMALL,
            width=15,
            anchor="w",
            bg=bg
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # Buttons
        btn_frame = tk.Frame(
            row,
            bg=bg
        )

        btn_frame.pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            btn_frame,
            text="✏ Edit",
            command=lambda x=expense_id: edit_expense(x)
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            btn_frame,
            text="🗑 Delete",
            command=lambda x=expense_id: delete_gui(x)
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        row_num += 1


# ===== Update Summary =====
def update_summary():

    total = get_total_expense()

    total_label.config(
        text=f"Total Expense      : ₹{total:.2f}"
    )

    count = get_transaction_count()

    transaction_label.config(
        text=f"Total Transactions : {count}"
    )


# ===== Refresh GUI =====
def refresh_gui():


    display_expenses()

    update_summary()


# ===== Add Expense =====
def add_expense_gui():

    category = category_entry.get().strip()
    amount = amount_entry.get().strip()
    date = date_entry.get().strip()

    if not category or not amount or not date:

        status_var.set(
            "Status : Please fill all fields"
        )

        return

    try:
        amount = float(amount)
    except ValueError:

        status_var.set(
            "Status : Amount must be a number"
        )

        return

    add_expense(
        category,
        date,
        amount
    )

    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

    status_var.set(
        "Status : Expense added successfully"
    )

    refresh_gui()


# Add Button (inside quick_add_frame)
add_btn = ttk.Button(
    quick_add_frame,
    text="ADD EXPENSE",
    command=add_expense_gui,
    style="Accent.TButton"
)
add_btn.grid(row=3, column=0, columnspan=2, pady=(15, 5))


# ===== Delete Expense =====
def delete_gui(expense_id):

    delete_expense(expense_id)

    status_var.set(
        "Status : Expense deleted successfully"
    )

    refresh_gui()


# ===== Edit Expense (Popup) =====
def edit_expense(expense_id):

    expenses_list = get_expenses()

    item = None

    for expense in expenses_list:

        if expense[0] == expense_id:
            item = expense
            break

    if item is None:
        return

    popup = tk.Toplevel(root)

    popup.title("Edit Expense")

    popup.geometry("400x300")

    popup.resizable(False, False)

    popup.grab_set()

    tk.Label(
        popup,
        text="EDIT EXPENSE",
        font=FONT_HEADER
    ).pack(pady=15)

    form = tk.Frame(popup)

    form.pack(pady=10)

    # Category
    tk.Label(
        form,
        text="Category :"
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=10
    )

    cat_entry = ttk.Entry(
        form,
        width=25
    )

    cat_entry.grid(
        row=0,
        column=1
    )

    cat_entry.insert(
        0,
        item[1]
    )

    # Amount
    tk.Label(
        form,
        text="Amount :"
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=10
    )

    amt_entry = ttk.Entry(
        form,
        width=25
    )

    amt_entry.grid(
        row=1,
        column=1
    )

    amt_entry.insert(
        0,
        str(item[3])
    )

    # Date
    tk.Label(
        form,
        text="Date :"
    ).grid(
        row=2,
        column=0,
        padx=10,
        pady=10
    )

    date_entry_popup = ttk.Entry(
        form,
        width=25
    )

    date_entry_popup.grid(
        row=2,
        column=1
    )

    date_entry_popup.insert(
        0,
        str(item[2])
    )

    def save_changes():

        category = cat_entry.get().strip()
        amount = amt_entry.get().strip()
        date = date_entry_popup.get().strip()

        if not category or not amount or not date:
            return

        try:
            amount = float(amount)
        except ValueError:
            return

        update_expense(
            expense_id,
            category,
            date,
            amount
        )

        popup.destroy()

        status_var.set(
            "Status : Expense updated successfully"
        )

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
    popup.geometry("900x550")
    popup.resizable(True, True)

    # Center the popup
    popup.update_idletasks()

    x = root.winfo_x() + (root.winfo_width() // 2) - (900 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (550 // 2)

    popup.geometry(f"+{x}+{y}")

    # ================= TITLE =================

    tk.Label(
        popup,
        text="EXPENSE HISTORY",
        font=FONT_HISTORY_TITLE
    ).pack(pady=15)

    # ================= TABLE FRAME =================

    table_frame = tk.Frame(popup)
    table_frame.pack(
        fill=tk.BOTH,
        expand=True,
        padx=25,
        pady=10
    )

    # ================= HEADINGS =================

    headings = [
        ("ID", 8),
        ("Category", 30),
        ("Amount", 18),
        ("Date", 18)
    ]

    heading_frame = tk.Frame(table_frame)
    heading_frame.pack(fill=tk.X)

    for head, width in headings:

        tk.Label(
            heading_frame,
            text=head,
            font=FONT_HEADING_BOLD,
            width=width,
            anchor="w"
        ).pack(
            side=tk.LEFT,
            padx=5
        )

    ttk.Separator(
        table_frame,
        orient="horizontal"
    ).pack(
        fill=tk.X,
        pady=5
    )

    # ================= SCROLLABLE AREA =================

    content_frame = tk.Frame(table_frame)
    content_frame.pack(
        fill=tk.BOTH,
        expand=True
    )

    canvas = tk.Canvas(
        content_frame,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        content_frame,
        orient="vertical",
        command=canvas.yview
    )

    history_frame = tk.Frame(canvas)

    canvas_window = canvas.create_window(
        (0, 0),
        window=history_frame,
        anchor="nw"
    )

    history_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True
    )

    scrollbar.pack(
        side=tk.RIGHT,
        fill=tk.Y
    )

    # Make inner frame same width as canvas
    def resize_history(event):

        canvas.itemconfig(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_history
    )

    # ================= LOAD DATABASE DATA =================

    data = get_expenses()

    for row_number, item in enumerate(data):

        # PostgreSQL structure:
        #
        # item[0] = ID
        # item[1] = title/category
        # item[2] = date
        # item[3] = amount

        expense_id = item[0]
        category = item[1]
        date = item[2]
        amount = item[3]

        # Alternating row background
        if row_number % 2 == 0:
            bg = "white"
        else:
            bg = "#f5f5f5"

        row = tk.Frame(
            history_frame,
            bg=bg
        )

        row.pack(
            fill=tk.X,
            pady=1
        )

        # ID
        tk.Label(
            row,
            text=expense_id,
            width=8,
            anchor="w",
            font=FONT_SMALL,
            bg=bg
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # Category
        tk.Label(
            row,
            text=category,
            width=30,
            anchor="w",
            font=FONT_SMALL,
            bg=bg
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # Amount
        tk.Label(
            row,
            text=f"₹{amount:.2f}",
            width=18,
            anchor="w",
            font=FONT_SMALL,
            bg=bg
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # Date
        tk.Label(
            row,
            text=str(date),
            width=18,
            anchor="w",
            font=FONT_SMALL,
            bg=bg
        ).pack(
            side=tk.LEFT,
            padx=5
        )

    # ================= MOUSE WHEEL =================

    def h_mousewheel(event):

        canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    canvas.bind(
        "<Enter>",
        lambda e: canvas.bind_all(
            "<MouseWheel>",
            h_mousewheel
        )
    )

    canvas.bind(
        "<Leave>",
        lambda e: canvas.unbind_all(
            "<MouseWheel>"
        )
    )


# History Button
history_btn = ttk.Button(
    history_btn_frame,
    text="VIEW EXPENSE HISTORY",
    command=view_history,
    style="Accent.TButton"
)

history_btn.pack()


# ===== Start GUI =====
refresh_gui()

root.mainloop()
