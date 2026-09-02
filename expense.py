import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
from decimal import Decimal

# Try to enable Windows DPI awareness for razor-sharp fonts
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from helper import (
    get_expenses,
    add_expense,
    update_expense,
    delete_expense,
    get_total_expense,
    get_transaction_count,
    get_today_expense,
    get_category_breakdown,
)
from fileop import load_expense

# ==============================================================================
# COLOR PALETTE & DESIGN SYSTEM
# ==============================================================================
THEME = {
    "bg_app": "#f1f5f9",           # Slate 100
    "header_bg": "#0f172a",        # Slate 900
    "header_fg": "#ffffff",
    "card_bg": "#ffffff",          # Pure white
    "card_border": "#e2e8f0",      # Slate 200
    "text_dark": "#0f172a",        # Slate 900
    "text_muted": "#64748b",       # Slate 500
    "text_light": "#94a3b8",       # Slate 400
    
    # Accent Colors
    "primary": "#4f46e5",          # Indigo 600
    "primary_hover": "#4338ca",    # Indigo 700
    "primary_light": "#eef2ff",    # Indigo 50
    
    "success": "#10b981",          # Emerald 500
    "success_hover": "#059669",
    "success_light": "#ecfdf5",
    
    "danger": "#ef4444",           # Rose 500
    "danger_hover": "#dc2626",
    "danger_light": "#fef2f2",
    
    "warning": "#f59e0b",          # Amber 500
    "warning_light": "#fffbeb",
    
    "info": "#0ea5e9",             # Sky 500
    "info_light": "#f0f9ff",
    
    "table_alt": "#f8fafc",        # Slate 50
    "table_select_bg": "#e0e7ff",  # Indigo 100
    "table_select_fg": "#1e1b4b",  # Indigo 950
}

FONT_FAMILY = "Segoe UI"
FONTS = {
    "title": (FONT_FAMILY, 15, "bold"),
    "subtitle": (FONT_FAMILY, 9),
    "kpi_val": (FONT_FAMILY, 16, "bold"),
    "kpi_lbl": (FONT_FAMILY, 9, "bold"),
    "section": (FONT_FAMILY, 11, "bold"),
    "label": (FONT_FAMILY, 9, "bold"),
    "body": (FONT_FAMILY, 9),
    "bold": (FONT_FAMILY, 9, "bold"),
    "btn": (FONT_FAMILY, 9, "bold"),
    "btn_sm": (FONT_FAMILY, 8, "bold"),
    "status": (FONT_FAMILY, 8),
    "mono": ("Consolas", 9),
}

DEFAULT_CATEGORIES = [
    "Food & Dining",
    "Shopping & Groceries",
    "Bills & Utilities",
    "Transportation & Fuel",
    "Entertainment & Leisure",
    "Health & Medical",
    "Office & Work",
    "Education & Courses",
    "Travel & Lodging",
    "Software & Subscriptions",
    "Home Maintenance",
    "Savings & Investment",
    "Miscellaneous",
]


# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================
class ExpenseTrackerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ExpenseFlow Pro — Financial Dashboard")
        self.root.geometry("1180x780")
        self.root.minsize(1040, 680)
        self.root.configure(bg=THEME["bg_app"])

        # State Variables
        self.all_expenses = []
        self.filtered_expenses = []
        self.selected_expense_id = None
        self.sort_column = "id"
        self.sort_descending = True

        self.setup_styles()
        self.build_ui()
        self.start_live_clock()
        self.refresh_all_data()

    # --------------------------------------------------------------------------
    # STYLING
    # --------------------------------------------------------------------------
    def setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Treeview styling
        self.style.configure(
            "Custom.Treeview",
            background=THEME["card_bg"],
            foreground=THEME["text_dark"],
            fieldbackground=THEME["card_bg"],
            rowheight=32,
            font=FONTS["body"],
            borderwidth=0,
        )
        self.style.map(
            "Custom.Treeview",
            background=[("selected", THEME["table_select_bg"])],
            foreground=[("selected", THEME["table_select_fg"])],
        )

        # Treeview Header
        self.style.configure(
            "Custom.Treeview.Heading",
            background=THEME["table_alt"],
            foreground=THEME["text_dark"],
            font=FONTS["bold"],
            padding=8,
            borderwidth=1,
            relief="flat",
        )
        self.style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#e2e8f0")],
            foreground=[("active", THEME["primary"])],
        )

        # Combobox styling
        self.style.configure(
            "TCombobox",
            padding=5,
            font=FONTS["body"],
        )

        # Scrollbar styling
        self.style.configure(
            "Vertical.TScrollbar",
            background=THEME["bg_app"],
            troughcolor=THEME["card_bg"],
            borderwidth=0,
            arrowsize=12,
        )

    # --------------------------------------------------------------------------
    # UI BUILD
    # --------------------------------------------------------------------------
    def build_ui(self):
        # Top Header Bar
        self.create_header()

        # KPI Summary Metrics Deck
        self.create_kpi_deck()

        # Main Content Area (Split Left: Quick Add & Stats | Right: Transactions)
        main_content = tk.Frame(self.root, bg=THEME["bg_app"])
        main_content.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 10))

        # Left Panel (Quick Add + Mini Breakdown)
        left_panel = tk.Frame(main_content, bg=THEME["bg_app"], width=360)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        left_panel.pack_propagate(False)

        self.create_quick_add_card(left_panel)
        self.create_breakdown_card(left_panel)

        # Right Panel (Toolbar + Table + Actions)
        right_panel = tk.Frame(main_content, bg=THEME["bg_app"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_table_card(right_panel)

        # Bottom Status Bar
        self.create_status_bar()

    # --------------------------------------------------------------------------
    # HEADER BAR
    # --------------------------------------------------------------------------
    def create_header(self):
        header = tk.Frame(self.root, bg=THEME["header_bg"], height=64)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Logo & App Title
        brand_frame = tk.Frame(header, bg=THEME["header_bg"])
        brand_frame.pack(side=tk.LEFT, padx=20, pady=8)

        logo_icon = tk.Label(
            brand_frame,
            text="💼",
            font=(FONT_FAMILY, 18),
            bg=THEME["header_bg"],
            fg="#ffffff",
        )
        logo_icon.pack(side=tk.LEFT, padx=(0, 10))

        title_box = tk.Frame(brand_frame, bg=THEME["header_bg"])
        title_box.pack(side=tk.LEFT)

        app_title = tk.Label(
            title_box,
            text="EXPENSEFLOW PRO",
            font=FONTS["title"],
            fg="#ffffff",
            bg=THEME["header_bg"],
        )
        app_title.pack(anchor="w")

        app_sub = tk.Label(
            title_box,
            text="Smart Financial Tracking & Dashboard",
            font=FONTS["subtitle"],
            fg=THEME["text_light"],
            bg=THEME["header_bg"],
        )
        app_sub.pack(anchor="w")

        # Right-side Header Tools (Live Time + Actions)
        header_tools = tk.Frame(header, bg=THEME["header_bg"])
        header_tools.pack(side=tk.RIGHT, padx=20)

        self.clock_label = tk.Label(
            header_tools,
            text="",
            font=FONTS["body"],
            fg="#e2e8f0",
            bg="#1e293b",
            padx=12,
            pady=4,
        )
        self.clock_label.pack(side=tk.LEFT, padx=(0, 10))

        export_btn = tk.Button(
            header_tools,
            text="📥 Export CSV",
            font=FONTS["btn_sm"],
            bg="#334155",
            fg="#ffffff",
            activebackground="#475569",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.export_csv,
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 8))

        history_btn = tk.Button(
            header_tools,
            text="📊 Full Analytics",
            font=FONTS["btn_sm"],
            bg=THEME["primary"],
            fg="#ffffff",
            activebackground=THEME["primary_hover"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.open_analytics_modal,
        )
        history_btn.pack(side=tk.LEFT)

    # --------------------------------------------------------------------------
    # KPI METRIC CARDS
    # --------------------------------------------------------------------------
    def create_kpi_deck(self):
        kpi_container = tk.Frame(self.root, bg=THEME["bg_app"])
        kpi_container.pack(fill=tk.X, padx=18, pady=14)

        cards_data = [
            ("TOTAL SPENDING", "₹0.00", "Across all records", THEME["primary"], THEME["primary_light"], "💰"),
            ("TODAY'S SPEND", "₹0.00", "Logged today", THEME["success"], THEME["success_light"], "📅"),
            ("TRANSACTIONS", "0", "Total recorded", THEME["info"], THEME["info_light"], "🧾"),
            ("TOP CATEGORY", "None", "Highest spending area", THEME["warning"], THEME["warning_light"], "🏷️"),
        ]

        self.kpi_value_labels = []

        for i, (title, val, sub, accent_color, bg_light, icon) in enumerate(cards_data):
            card = tk.Frame(
                kpi_container,
                bg=THEME["card_bg"],
                highlightbackground=THEME["card_border"],
                highlightthickness=1,
                padx=14,
                pady=10,
            )
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i == 0 else 10, 0))

            # Left Icon Pill
            top_row = tk.Frame(card, bg=THEME["card_bg"])
            top_row.pack(fill=tk.X)

            icon_lbl = tk.Label(
                top_row,
                text=icon,
                font=(FONT_FAMILY, 14),
                bg=bg_light,
                fg=accent_color,
                padx=6,
                pady=2,
            )
            icon_lbl.pack(side=tk.LEFT)

            title_lbl = tk.Label(
                top_row,
                text=title,
                font=FONTS["kpi_lbl"],
                fg=THEME["text_muted"],
                bg=THEME["card_bg"],
            )
            title_lbl.pack(side=tk.LEFT, padx=8)

            # Value Label
            val_lbl = tk.Label(
                card,
                text=val,
                font=FONTS["kpi_val"],
                fg=THEME["text_dark"],
                bg=THEME["card_bg"],
                anchor="w",
            )
            val_lbl.pack(fill=tk.X, pady=(4, 0))
            self.kpi_value_labels.append(val_lbl)

            # Subtitle
            sub_lbl = tk.Label(
                card,
                text=sub,
                font=FONTS["subtitle"],
                fg=THEME["text_light"],
                bg=THEME["card_bg"],
                anchor="w",
            )
            sub_lbl.pack(fill=tk.X)

    # --------------------------------------------------------------------------
    # LEFT PANEL: QUICK ADD EXPENSE
    # --------------------------------------------------------------------------
    def create_quick_add_card(self, parent):
        card = tk.Frame(
            parent,
            bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        card.pack(fill=tk.X, pady=(0, 12))

        # Card Title
        header_box = tk.Frame(card, bg=THEME["card_bg"])
        header_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            header_box,
            text="⚡ QUICK ADD EXPENSE",
            font=FONTS["section"],
            fg=THEME["text_dark"],
            bg=THEME["card_bg"],
        ).pack(side=tk.LEFT)

        # 1. Category Field
        tk.Label(
            card,
            text="Category / Description *",
            font=FONTS["label"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(anchor="w", pady=(2, 3))

        self.cat_var = tk.StringVar()
        self.category_cb = ttk.Combobox(
            card,
            textvariable=self.cat_var,
            values=DEFAULT_CATEGORIES,
            font=FONTS["body"],
        )
        self.category_cb.pack(fill=tk.X, pady=(0, 10))
        self.category_cb.set(DEFAULT_CATEGORIES[0])

        # 2. Amount Field
        tk.Label(
            card,
            text="Amount (₹) *",
            font=FONTS["label"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(anchor="w", pady=(2, 3))

        self.amt_entry = ttk.Entry(card, font=FONTS["body"])
        self.amt_entry.pack(fill=tk.X, pady=(0, 6))

        # Quick Amount Chips (+100, +500, +1000, +2000)
        chip_frame = tk.Frame(card, bg=THEME["card_bg"])
        chip_frame.pack(fill=tk.X, pady=(0, 10))

        for chip_val in [100, 500, 1000, 2000]:
            btn = tk.Button(
                chip_frame,
                text=f"+₹{chip_val}",
                font=FONTS["btn_sm"],
                bg=THEME["table_alt"],
                fg=THEME["primary"],
                activebackground=THEME["primary_light"],
                activeforeground=THEME["primary"],
                relief="flat",
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda v=chip_val: self.add_chip_amount(v),
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))

        # 3. Date Field
        date_header = tk.Frame(card, bg=THEME["card_bg"])
        date_header.pack(fill=tk.X, pady=(2, 3))

        tk.Label(
            date_header,
            text="Date (YYYY-MM-DD) *",
            font=FONTS["label"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(side=tk.LEFT)

        today_btn = tk.Button(
            date_header,
            text="Today",
            font=FONTS["btn_sm"],
            bg=THEME["table_alt"],
            fg=THEME["text_dark"],
            relief="flat",
            bd=0,
            padx=6,
            pady=1,
            cursor="hand2",
            command=self.set_date_today,
        )
        today_btn.pack(side=tk.RIGHT)

        yesterday_btn = tk.Button(
            date_header,
            text="Yesterday",
            font=FONTS["btn_sm"],
            bg=THEME["table_alt"],
            fg=THEME["text_dark"],
            relief="flat",
            bd=0,
            padx=6,
            pady=1,
            cursor="hand2",
            command=self.set_date_yesterday,
        )
        yesterday_btn.pack(side=tk.RIGHT, padx=(0, 4))

        self.date_entry = ttk.Entry(card, font=FONTS["body"])
        self.date_entry.pack(fill=tk.X, pady=(0, 14))
        self.set_date_today()

        # Action Buttons
        btn_box = tk.Frame(card, bg=THEME["card_bg"])
        btn_box.pack(fill=tk.X)

        add_btn = tk.Button(
            btn_box,
            text="➕  ADD EXPENSE",
            font=FONTS["btn"],
            bg=THEME["primary"],
            fg="#ffffff",
            activebackground=THEME["primary_hover"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            pady=8,
            cursor="hand2",
            command=self.handle_add_expense,
        )
        add_btn.pack(fill=tk.X, pady=(0, 6))

        clear_btn = tk.Button(
            btn_box,
            text="Clear Form",
            font=FONTS["btn_sm"],
            bg=THEME["table_alt"],
            fg=THEME["text_muted"],
            activebackground="#e2e8f0",
            activeforeground=THEME["text_dark"],
            relief="flat",
            bd=0,
            pady=4,
            cursor="hand2",
            command=self.clear_form,
        )
        clear_btn.pack(fill=tk.X)

    def add_chip_amount(self, increment):
        current_text = self.amt_entry.get().strip()
        try:
            val = float(current_text) if current_text else 0.0
            new_val = val + increment
            self.amt_entry.delete(0, tk.END)
            self.amt_entry.insert(0, f"{new_val:.2f}" if new_val % 1 else f"{int(new_val)}")
        except ValueError:
            self.amt_entry.delete(0, tk.END)
            self.amt_entry.insert(0, str(increment))

    def set_date_today(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

    def set_date_yesterday(self):
        self.date_entry.delete(0, tk.END)
        yest = date.today() - timedelta(days=1)
        self.date_entry.insert(0, yest.strftime("%Y-%m-%d"))

    def clear_form(self):
        self.category_cb.set(DEFAULT_CATEGORIES[0])
        self.amt_entry.delete(0, tk.END)
        self.set_date_today()
        self.set_status("Form cleared", "info")

    # --------------------------------------------------------------------------
    # LEFT PANEL: CATEGORY BREAKDOWN MINI CARD
    # --------------------------------------------------------------------------
    def create_breakdown_card(self, parent):
        self.breakdown_card = tk.Frame(
            parent,
            bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        self.breakdown_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self.breakdown_card,
            text="📊 SPENDING BY CATEGORY",
            font=FONTS["section"],
            fg=THEME["text_dark"],
            bg=THEME["card_bg"],
        ).pack(anchor="w", pady=(0, 8))

        # Canvas container for scrollable category bars
        self.breakdown_content = tk.Frame(self.breakdown_card, bg=THEME["card_bg"])
        self.breakdown_content.pack(fill=tk.BOTH, expand=True)

    def render_breakdown(self, breakdown_data):
        for widget in self.breakdown_content.winfo_children():
            widget.destroy()

        if not breakdown_data:
            empty_lbl = tk.Label(
                self.breakdown_content,
                text="No expenses recorded yet.",
                font=FONTS["body"],
                fg=THEME["text_muted"],
                bg=THEME["card_bg"],
            )
            empty_lbl.pack(pady=20)
            return

        total_sum = sum(float(item[1]) for item in breakdown_data) or 1.0

        # Show top 5 categories
        for item in breakdown_data[:5]:
            cat_name = item[0]
            cat_amount = float(item[1])
            percentage = (cat_amount / total_sum) * 100

            row = tk.Frame(self.breakdown_content, bg=THEME["card_bg"])
            row.pack(fill=tk.X, pady=3)

            # Label Row (Category + Amount)
            info_row = tk.Frame(row, bg=THEME["card_bg"])
            info_row.pack(fill=tk.X)

            cat_lbl = tk.Label(
                info_row,
                text=cat_name[:18] + ("..." if len(cat_name) > 18 else ""),
                font=FONTS["bold"],
                fg=THEME["text_dark"],
                bg=THEME["card_bg"],
            )
            cat_lbl.pack(side=tk.LEFT)

            amt_lbl = tk.Label(
                info_row,
                text=f"₹{cat_amount:,.2f} ({percentage:.0f}%)",
                font=FONTS["body"],
                fg=THEME["text_muted"],
                bg=THEME["card_bg"],
            )
            amt_lbl.pack(side=tk.RIGHT)

            # Progress Bar (Canvas)
            bar_canvas = tk.Canvas(
                row,
                height=6,
                bg="#f1f5f9",
                highlightthickness=0,
                bd=0,
            )
            bar_canvas.pack(fill=tk.X, pady=(2, 4))
            
            # Fill width calculation
            def draw_bar(c=bar_canvas, p=percentage):
                c.update_idletasks()
                w = c.winfo_width()
                if w > 1:
                    fill_w = max(4, int(w * (p / 100.0)))
                    c.create_rectangle(0, 0, fill_w, 6, fill=THEME["primary"], outline="")

            bar_canvas.bind("<Configure>", lambda e, c=bar_canvas, p=percentage: draw_bar(c, p))

    # --------------------------------------------------------------------------
    # RIGHT PANEL: TRANSACTIONS TABLE & TOOLBAR
    # --------------------------------------------------------------------------
    def create_table_card(self, parent):
        card = tk.Frame(
            parent,
            bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        card.pack(fill=tk.BOTH, expand=True)

        # Toolbar Header
        toolbar = tk.Frame(card, bg=THEME["card_bg"])
        toolbar.pack(fill=tk.X, pady=(0, 10))

        # Title & Count
        title_box = tk.Frame(toolbar, bg=THEME["card_bg"])
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="📑 TRANSACTIONS",
            font=FONTS["section"],
            fg=THEME["text_dark"],
            bg=THEME["card_bg"],
        ).pack(side=tk.LEFT)

        self.table_count_lbl = tk.Label(
            title_box,
            text="(0 records)",
            font=FONTS["subtitle"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        )
        self.table_count_lbl.pack(side=tk.LEFT, padx=6)

        # Right-side Toolbar Controls: Search, Category Filter, Sort
        tools_box = tk.Frame(toolbar, bg=THEME["card_bg"])
        tools_box.pack(side=tk.RIGHT)

        # Search Bar
        tk.Label(
            tools_box,
            text="🔍",
            font=FONTS["body"],
            bg=THEME["card_bg"],
        ).pack(side=tk.LEFT, padx=(0, 2))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.apply_filters())

        search_entry = ttk.Entry(
            tools_box,
            textvariable=self.search_var,
            width=20,
            font=FONTS["body"],
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Filter by Category
        tk.Label(
            tools_box,
            text="Category:",
            font=FONTS["body"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.filter_cat_var = tk.StringVar(value="All Categories")
        self.filter_cat_cb = ttk.Combobox(
            tools_box,
            textvariable=self.filter_cat_var,
            state="readonly",
            width=16,
            font=FONTS["body"],
        )
        self.filter_cat_cb.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_cat_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Sort Dropdown
        tk.Label(
            tools_box,
            text="Sort:",
            font=FONTS["body"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.sort_var = tk.StringVar(value="Date (Newest)")
        sort_cb = ttk.Combobox(
            tools_box,
            textvariable=self.sort_var,
            values=[
                "Date (Newest)",
                "Date (Oldest)",
                "Amount (High to Low)",
                "Amount (Low to High)",
                "Category (A-Z)",
            ],
            state="readonly",
            width=16,
            font=FONTS["body"],
        )
        sort_cb.pack(side=tk.LEFT)
        sort_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Table Frame (Treeview + Scrollbar)
        tree_frame = tk.Frame(card, bg=THEME["card_bg"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "category", "date", "amount")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        # Configure Headings
        self.tree.heading("id", text="# ID", command=lambda: self.set_sort_column("id"))
        self.tree.heading("category", text="Category / Description", command=lambda: self.set_sort_column("category"))
        self.tree.heading("date", text="Date", command=lambda: self.set_sort_column("date"))
        self.tree.heading("amount", text="Amount (₹)", command=lambda: self.set_sort_column("amount"))

        # Configure Column Widths & Alignments
        self.tree.column("id", width=65, anchor="center", stretch=False)
        self.tree.column("category", width=260, anchor="w")
        self.tree.column("date", width=120, anchor="center", stretch=False)
        self.tree.column("amount", width=140, anchor="e", stretch=False)

        # Alternating row colors
        self.tree.tag_configure("evenrow", background=THEME["card_bg"])
        self.tree.tag_configure("oddrow", background=THEME["table_alt"])

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.tree.yview,
            style="Vertical.TScrollbar",
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Event Bindings
        self.tree.bind("<Double-1>", lambda e: self.open_edit_selected())
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Context Menu
        self.context_menu = tk.Menu(self.root, tearoff=0, font=FONTS["body"])
        self.context_menu.add_command(label="✏  Edit Expense", command=self.open_edit_selected)
        self.context_menu.add_command(label="🗑  Delete Expense", command=self.handle_delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋  Copy Amount", command=self.copy_selected_amount)
        self.context_menu.add_command(label="📑  Duplicate as New", command=self.duplicate_selected)

        # Bottom Action Bar (Edit, Delete, Refresh, Export)
        actions_bar = tk.Frame(card, bg=THEME["card_bg"])
        actions_bar.pack(fill=tk.X, pady=(10, 0))

        self.edit_btn = tk.Button(
            actions_bar,
            text="✏  Edit Selected",
            font=FONTS["btn_sm"],
            bg=THEME["table_alt"],
            fg=THEME["text_dark"],
            activebackground="#e2e8f0",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            state=tk.DISABLED,
            cursor="hand2",
            command=self.open_edit_selected,
        )
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.del_btn = tk.Button(
            actions_bar,
            text="🗑  Delete Selected",
            font=FONTS["btn_sm"],
            bg=THEME["danger_light"],
            fg=THEME["danger"],
            activebackground=THEME["danger"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            state=tk.DISABLED,
            cursor="hand2",
            command=self.handle_delete_selected,
        )
        self.del_btn.pack(side=tk.LEFT, padx=(0, 8))

        refresh_btn = tk.Button(
            actions_bar,
            text="🔄  Refresh",
            font=FONTS["btn_sm"],
            bg=THEME["table_alt"],
            fg=THEME["text_dark"],
            activebackground="#e2e8f0",
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.refresh_all_data,
        )
        refresh_btn.pack(side=tk.LEFT)

        # Hint text
        tk.Label(
            actions_bar,
            text="💡 Tip: Double-click row to edit • Right-click for options",
            font=FONTS["subtitle"],
            fg=THEME["text_light"],
            bg=THEME["card_bg"],
        ).pack(side=tk.RIGHT)

    # --------------------------------------------------------------------------
    # STATUS BAR
    # --------------------------------------------------------------------------
    def create_status_bar(self):
        status_frame = tk.Frame(self.root, bg="#1e293b", height=28)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_dot = tk.Label(
            status_frame,
            text="●",
            font=(FONT_FAMILY, 8),
            fg=THEME["success"],
            bg="#1e293b",
        )
        self.status_dot.pack(side=tk.LEFT, padx=(12, 4))

        self.status_lbl = tk.Label(
            status_frame,
            text="Ready",
            font=FONTS["status"],
            fg="#94a3b8",
            bg="#1e293b",
        )
        self.status_lbl.pack(side=tk.LEFT)

        self.db_status_lbl = tk.Label(
            status_frame,
            text="PostgreSQL Connected 🟢",
            font=FONTS["status"],
            fg="#94a3b8",
            bg="#1e293b",
        )
        self.db_status_lbl.pack(side=tk.RIGHT, padx=12)

    def set_status(self, message: str, level: str = "info"):
        level_colors = {
            "success": THEME["success"],
            "danger": THEME["danger"],
            "warning": THEME["warning"],
            "info": "#60a5fa",
        }
        color = level_colors.get(level, "#94a3b8")
        self.status_dot.config(fg=color)
        self.status_lbl.config(text=message, fg="#ffffff" if level in ("success", "danger") else "#94a3b8")

    # --------------------------------------------------------------------------
    # LIVE CLOCK
    # --------------------------------------------------------------------------
    def start_live_clock(self):
        now = datetime.now()
        date_part = now.strftime("%a, %d %b %Y")
        time_part = now.strftime("%H:%M:%S")
        time_str = f"📅 {date_part}  •  🕒 {time_part}"
        self.clock_label.config(text=time_str)
        self.root.after(1000, self.start_live_clock)

    # --------------------------------------------------------------------------
    # DATA HANDLING & REFRESH
    # --------------------------------------------------------------------------
    def refresh_all_data(self):
        try:
            self.all_expenses = get_expenses()
            self.db_status_lbl.config(text="PostgreSQL Connected 🟢", fg="#94a3b8")
        except Exception as e:
            self.all_expenses = []
            self.db_status_lbl.config(text="Database Error 🔴", fg=THEME["danger"])
            self.set_status(f"Database error: {e}", "danger")

        # Update Category Filter Dropdown values
        categories = sorted(list({str(item[1]) for item in self.all_expenses if item[1]}))
        filter_options = ["All Categories"] + categories
        self.filter_cat_cb["values"] = filter_options
        if self.filter_cat_var.get() not in filter_options:
            self.filter_cat_var.set("All Categories")

        # Update KPI Cards
        self.update_kpis()

        # Update Breakdown
        try:
            breakdown = get_category_breakdown()
            self.render_breakdown(breakdown)
        except Exception:
            self.render_breakdown([])

        # Filter & Render Table
        self.apply_filters()
        self.set_status(f"Synced {len(self.all_expenses)} records", "success")

    def update_kpis(self):
        try:
            total_spend = get_total_expense()
            tx_count = get_transaction_count()
            today_spend = get_today_expense()
            breakdown = get_category_breakdown()
            top_cat = breakdown[0][0] if breakdown else "None"
        except Exception:
            total_spend = sum(float(x[3]) for x in self.all_expenses)
            tx_count = len(self.all_expenses)
            today_spend = 0.0
            top_cat = "None"

        # Update Cards
        self.kpi_value_labels[0].config(text=f"₹{float(total_spend):,.2f}")
        self.kpi_value_labels[1].config(text=f"₹{float(today_spend):,.2f}")
        self.kpi_value_labels[2].config(text=f"{tx_count:,}")
        self.kpi_value_labels[3].config(text=f"{top_cat[:14]}")

    def apply_filters(self):
        search_term = self.search_var.get().strip().lower()
        cat_filter = self.filter_cat_var.get()
        sort_mode = self.sort_var.get()

        filtered = []
        for item in self.all_expenses:
            # item: (id, title, date, amount)
            exp_id, title, exp_date, amount = item
            str_title = str(title).lower()
            str_amount = str(amount)
            str_date = str(exp_date)

            # Category filter
            if cat_filter != "All Categories" and str(title) != cat_filter:
                continue

            # Search keyword match
            if search_term and (search_term not in str_title and search_term not in str_amount and search_term not in str_date):
                continue

            filtered.append(item)

        # Sorting
        if sort_mode == "Date (Newest)":
            filtered.sort(key=lambda x: str(x[2]), reverse=True)
        elif sort_mode == "Date (Oldest)":
            filtered.sort(key=lambda x: str(x[2]), reverse=False)
        elif sort_mode == "Amount (High to Low)":
            filtered.sort(key=lambda x: float(x[3]), reverse=True)
        elif sort_mode == "Amount (Low to High)":
            filtered.sort(key=lambda x: float(x[3]), reverse=False)
        elif sort_mode == "Category (A-Z)":
            filtered.sort(key=lambda x: str(x[1]).lower())

        self.filtered_expenses = filtered
        self.render_table()

    def set_sort_column(self, col):
        if self.sort_column == col:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = col
            self.sort_descending = False

        arrow = " ▼" if self.sort_descending else " ▲"
        headers = {
            "id": "# ID",
            "category": "Category / Description",
            "date": "Date",
            "amount": "Amount (₹)",
        }
        for c, name in headers.items():
            self.tree.heading(c, text=name + (arrow if c == col else ""))

        if col == "id":
            self.filtered_expenses.sort(key=lambda x: int(x[0]), reverse=self.sort_descending)
        elif col == "category":
            self.filtered_expenses.sort(key=lambda x: str(x[1]).lower(), reverse=self.sort_descending)
        elif col == "date":
            self.filtered_expenses.sort(key=lambda x: str(x[2]), reverse=self.sort_descending)
        elif col == "amount":
            self.filtered_expenses.sort(key=lambda x: float(x[3]), reverse=self.sort_descending)

        self.render_table()

    def render_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_filtered_amt = 0.0

        for idx, item in enumerate(self.filtered_expenses):
            exp_id, title, exp_date, amount = item
            amt_float = float(amount)
            total_filtered_amt += amt_float

            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            formatted_amt = f"₹{amt_float:,.2f}"

            # Nicely formatted date
            try:
                if isinstance(exp_date, (datetime, date)):
                    date_display = exp_date.strftime("%d %b %Y")
                else:
                    date_display = str(exp_date)
            except Exception:
                date_display = str(exp_date)

            self.tree.insert(
                "",
                tk.END,
                iid=str(exp_id),
                values=(exp_id, title, date_display, formatted_amt),
                tags=(tag,),
            )

        self.table_count_lbl.config(
            text=f"({len(self.filtered_expenses)} shown • Total: ₹{total_filtered_amt:,.2f})"
        )
        self.edit_btn.config(state=tk.DISABLED)
        self.del_btn.config(state=tk.DISABLED)
        self.selected_expense_id = None

    # --------------------------------------------------------------------------
    # SELECTION & ACTIONS
    # --------------------------------------------------------------------------
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_expense_id = int(selected[0])
            self.edit_btn.config(state=tk.NORMAL)
            self.del_btn.config(state=tk.NORMAL)
        else:
            self.selected_expense_id = None
            self.edit_btn.config(state=tk.DISABLED)
            self.del_btn.config(state=tk.DISABLED)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.on_tree_select(None)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_amount(self):
        if not self.selected_expense_id:
            return
        for exp in self.all_expenses:
            if exp[0] == self.selected_expense_id:
                self.root.clipboard_clear()
                self.root.clipboard_append(str(exp[3]))
                self.set_status(f"Copied amount ₹{exp[3]} to clipboard", "info")
                break

    def duplicate_selected(self):
        if not self.selected_expense_id:
            return
        for exp in self.all_expenses:
            if exp[0] == self.selected_expense_id:
                self.category_cb.set(exp[1])
                self.amt_entry.delete(0, tk.END)
                self.amt_entry.insert(0, str(exp[3]))
                self.set_date_today()
                self.set_status(f"Loaded '{exp[1]}' details into Add Form", "info")
                break

    # --------------------------------------------------------------------------
    # ADD EXPENSE
    # --------------------------------------------------------------------------
    def handle_add_expense(self):
        category = self.cat_var.get().strip()
        amount_str = self.amt_entry.get().strip()
        date_str = self.date_entry.get().strip()

        if not category:
            messagebox.showwarning("Missing Information", "Please enter or select a category.")
            self.category_cb.focus()
            return

        if not amount_str:
            messagebox.showwarning("Missing Information", "Please enter an amount.")
            self.amt_entry.focus()
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for amount.")
            self.amt_entry.focus()
            return

        if not date_str:
            messagebox.showwarning("Missing Information", "Please specify a date.")
            self.date_entry.focus()
            return

        try:
            add_expense(category, date_str, amount)
            self.amt_entry.delete(0, tk.END)
            self.refresh_all_data()
            self.set_status(f"✅ Added ₹{amount:,.2f} for '{category}' successfully!", "success")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save expense:\n{e}")
            self.set_status(f"Error adding expense: {e}", "danger")

    # --------------------------------------------------------------------------
    # DELETE EXPENSE
    # --------------------------------------------------------------------------
    def handle_delete_selected(self):
        if not self.selected_expense_id:
            return

        item = None
        for exp in self.all_expenses:
            if exp[0] == self.selected_expense_id:
                item = exp
                break

        if not item:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this expense record?\n\n"
            f"ID: #{item[0]}\n"
            f"Category: {item[1]}\n"
            f"Date: {item[2]}\n"
            f"Amount: ₹{float(item[3]):,.2f}",
            icon="warning",
        )

        if confirm:
            try:
                delete_expense(self.selected_expense_id)
                self.refresh_all_data()
                self.set_status(f"🗑 Deleted expense #{item[0]} successfully", "warning")
            except Exception as e:
                messagebox.showerror("Delete Failed", f"Could not delete expense:\n{e}")

    # --------------------------------------------------------------------------
    # EDIT EXPENSE (MODERN POPUP)
    # --------------------------------------------------------------------------
    def open_edit_selected(self):
        if not self.selected_expense_id:
            return

        item = None
        for exp in self.all_expenses:
            if exp[0] == self.selected_expense_id:
                item = exp
                break

        if not item:
            return

        # Modal Window
        modal = tk.Toplevel(self.root)
        modal.title(f"Edit Expense #{item[0]}")
        modal.geometry("440x420")
        modal.resizable(False, False)
        modal.configure(bg=THEME["card_bg"])
        modal.transient(self.root)
        modal.grab_set()

        # Center modal relative to root
        modal.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width() // 2) - 220
        ry = self.root.winfo_y() + (self.root.winfo_height() // 2) - 210
        modal.geometry(f"+{max(0, rx)}+{max(0, ry)}")

        # Modal Header
        m_header = tk.Frame(modal, bg=THEME["header_bg"], height=55)
        m_header.pack(fill=tk.X)
        m_header.pack_propagate(False)

        tk.Label(
            m_header,
            text=f"✏ EDIT EXPENSE #{item[0]}",
            font=FONTS["section"],
            fg="#ffffff",
            bg=THEME["header_bg"],
        ).pack(side=tk.LEFT, padx=18, pady=14)

        # Form Body
        body = tk.Frame(modal, bg=THEME["card_bg"], padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Category
        tk.Label(
            body,
            text="Category / Description *",
            font=FONTS["label"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(anchor="w", pady=(0, 4))

        edit_cat_cb = ttk.Combobox(
            body,
            values=DEFAULT_CATEGORIES,
            font=FONTS["body"],
        )
        edit_cat_cb.pack(fill=tk.X, pady=(0, 12))
        edit_cat_cb.set(str(item[1]))

        # Amount
        tk.Label(
            body,
            text="Amount (₹) *",
            font=FONTS["label"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(anchor="w", pady=(0, 4))

        edit_amt = ttk.Entry(body, font=FONTS["body"])
        edit_amt.pack(fill=tk.X, pady=(0, 12))
        edit_amt.insert(0, str(item[3]))

        # Date
        tk.Label(
            body,
            text="Date (YYYY-MM-DD) *",
            font=FONTS["label"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"],
        ).pack(anchor="w", pady=(0, 4))

        edit_date = ttk.Entry(body, font=FONTS["body"])
        edit_date.pack(fill=tk.X, pady=(0, 20))
        edit_date.insert(0, str(item[2]))

        # Modal Actions
        btn_row = tk.Frame(body, bg=THEME["card_bg"])
        btn_row.pack(fill=tk.X)

        def save_edits():
            new_cat = edit_cat_cb.get().strip()
            new_amt_str = edit_amt.get().strip()
            new_date = edit_date.get().strip()

            if not new_cat or not new_amt_str or not new_date:
                messagebox.showwarning("Missing Fields", "Please complete all fields.", parent=modal)
                return

            try:
                new_amt = float(new_amt_str)
                if new_amt <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid positive number.", parent=modal)
                return

            try:
                update_expense(item[0], new_cat, new_date, new_amt)
                modal.destroy()
                self.refresh_all_data()
                self.set_status(f"Updated expense #{item[0]} successfully", "success")
            except Exception as err:
                messagebox.showerror("Update Error", f"Failed to update expense:\n{err}", parent=modal)

        save_btn = tk.Button(
            btn_row,
            text="💾 Save Changes",
            font=FONTS["btn"],
            bg=THEME["primary"],
            fg="#ffffff",
            activebackground=THEME["primary_hover"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=save_edits,
        )
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))

        cancel_btn = tk.Button(
            btn_row,
            text="Cancel",
            font=FONTS["btn_sm"],
            bg=THEME["table_alt"],
            fg=THEME["text_dark"],
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=modal.destroy,
        )
        cancel_btn.pack(side=tk.RIGHT)

    # --------------------------------------------------------------------------
    # FULL ANALYTICS & HISTORY MODAL
    # --------------------------------------------------------------------------
    def open_analytics_modal(self):
        modal = tk.Toplevel(self.root)
        modal.title("ExpenseFlow Pro — Comprehensive Financial Analytics")
        modal.geometry("980x620")
        modal.minsize(850, 500)
        modal.configure(bg=THEME["bg_app"])
        modal.transient(self.root)

        # Modal Header
        m_header = tk.Frame(modal, bg=THEME["header_bg"], height=60)
        m_header.pack(fill=tk.X)
        m_header.pack_propagate(False)

        tk.Label(
            m_header,
            text="📊 COMPREHENSIVE EXPENSE HISTORY & ANALYTICS",
            font=FONTS["section"],
            fg="#ffffff",
            bg=THEME["header_bg"],
        ).pack(side=tk.LEFT, padx=20, pady=16)

        # Content Deck
        container = tk.Frame(modal, bg=THEME["bg_app"], padx=20, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        # Top Summary Bar inside modal
        summary_card = tk.Frame(
            container,
            bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"],
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        summary_card.pack(fill=tk.X, pady=(0, 14))

        total_val = sum(float(x[3]) for x in self.all_expenses)
        avg_val = (total_val / len(self.all_expenses)) if self.all_expenses else 0.0

        tk.Label(
            summary_card,
            text=f"Total Expenses: ₹{total_val:,.2f}   •   Total Transactions: {len(self.all_expenses)}   •   Average Spend: ₹{avg_val:,.2f}",
            font=FONTS["bold"],
            fg=THEME["text_dark"],
            bg=THEME["card_bg"],
        ).pack(side=tk.LEFT)

        # Table in modal
        table_card = tk.Frame(
            container,
            bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"],
            highlightthickness=1,
            padx=12,
            pady=12,
        )
        table_card.pack(fill=tk.BOTH, expand=True)

        m_tree = ttk.Treeview(
            table_card,
            columns=("id", "category", "date", "amount"),
            show="headings",
            style="Custom.Treeview",
        )
        m_tree.heading("id", text="# ID")
        m_tree.heading("category", text="Category / Description")
        m_tree.heading("date", text="Date")
        m_tree.heading("amount", text="Amount (₹)")

        m_tree.column("id", width=70, anchor="center")
        m_tree.column("category", width=340, anchor="w")
        m_tree.column("date", width=140, anchor="center")
        m_tree.column("amount", width=160, anchor="e")

        m_scroll = ttk.Scrollbar(table_card, orient="vertical", command=m_tree.yview)
        m_tree.configure(yscrollcommand=m_scroll.set)

        m_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        m_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for i, item in enumerate(self.all_expenses):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            m_tree.insert(
                "",
                tk.END,
                values=(item[0], item[1], str(item[2]), f"₹{float(item[3]):,.2f}"),
                tags=(tag,),
            )

        m_tree.tag_configure("evenrow", background=THEME["card_bg"])
        m_tree.tag_configure("oddrow", background=THEME["table_alt"])

    # --------------------------------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------------------------------
    def export_csv(self):
        if not self.all_expenses:
            messagebox.showinfo("Export CSV", "No expense data available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")],
            title="Export Expenses to CSV",
            initialfile=f"Expenses_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Expense ID", "Category / Description", "Date", "Amount (INR)"])
                for item in self.all_expenses:
                    writer.writerow([item[0], item[1], item[2], f"{float(item[3]):.2f}"])

            messagebox.showinfo("Export Successful", f"Expenses exported successfully to:\n{file_path}")
            self.set_status(f"Exported {len(self.all_expenses)} records to CSV", "success")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not write CSV file:\n{e}")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    load_expense()
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
