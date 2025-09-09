import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import sqlite3
import random
import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

class DatabaseManager:
    
    def __init__(self, db_name="rental_inventory.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Create rentals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                receipt_ref TEXT UNIQUE,
                product_type TEXT,
                product_code TEXT,
                no_days INTEGER,
                cost_per_day REAL,
                account_open TEXT,
                app_date DATE,
                next_credit_review DATE,
                last_credit_review INTEGER,
                date_rev DATE,
                credit_limit TEXT,
                credit_check TEXT,
                sett_due_day INTEGER,
                payment_due TEXT,
                discount REAL,
                deposit TEXT,
                pay_due_day TEXT,
                payment_method TEXT,
                check_credit INTEGER,
                term_agreed INTEGER,
                account_on_hold INTEGER,
                restrict_mailing INTEGER,
                tax REAL,
                subtotal REAL,
                total REAL,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        ''')
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_type TEXT NOT NULL,
                product_code TEXT UNIQUE,
                cost_per_day REAL,
                available_quantity INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Available'
            )
        ''')
        
        # Insert default products if they don't exist
        default_products = [
            ('Car', 'CAR452', 12.00, 5),
            ('Van', 'VAN775', 19.00, 3),
            ('Minibus', 'MIN334', 12.00, 2),
            ('Truck', 'TRK7483', 15.00, 2)
        ]
        
        for product in default_products:
            cursor.execute('''
                INSERT OR IGNORE INTO products (product_type, product_code, cost_per_day, available_quantity)
                VALUES (?, ?, ?, ?)
            ''', product)
        
        conn.commit()
        conn.close()
        
    def save_rental(self, rental_data):
        """Save rental data to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rentals (
                customer_id, receipt_ref, product_type, product_code, no_days, cost_per_day,
                account_open, app_date, next_credit_review, last_credit_review, date_rev,
                credit_limit, credit_check, sett_due_day, payment_due, discount, deposit,
                pay_due_day, payment_method, check_credit, term_agreed, account_on_hold,
                restrict_mailing, tax, subtotal, total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rental_data)
        
        conn.commit()
        conn.close()
    
    def get_all_rentals(self):
        """Get all rental records"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rentals ORDER BY created_date DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_rentals(self, search_term):
        """Search rentals by receipt reference or product type"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM rentals 
            WHERE receipt_ref LIKE ? OR product_type LIKE ?
            ORDER BY created_date DESC
        ''', (f'%{search_term}%', f'%{search_term}%'))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_customers(self):
        """Get all customers"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY customer_name')
        results = cursor.fetchall()
        conn.close()
    
    # New methods for product management
    def add_product(self, product_type, product_code, cost_per_day, available_quantity):
        """Add a new product to the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO products (product_type, product_code, cost_per_day, available_quantity)
                VALUES (?, ?, ?, ?)
            ''', (product_type, product_code, cost_per_day, available_quantity))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Product code already exists.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
            return False
        finally:
            conn.close()
        
    def update_product(self, product_id, product_type, product_code, cost_per_day, available_quantity, status):
        """Update an existing product's details."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE products
                SET product_type = ?, product_code = ?, cost_per_day = ?, available_quantity = ?, status = ?
                WHERE product_id = ?
            ''', (product_type, product_code, cost_per_day, available_quantity, status, product_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Product code already exists for another product.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")
            return False
        finally:
            conn.close()    
    
    def delete_product(self, product_id):
        """Delete a product from the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
            conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_all_products(self):
        """Get all products from the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY product_type, product_code')
        results = cursor.fetchall()
        conn.close()
        return results
    

class ImprovedRentalInventory:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Rental Inventory Management System")
        self.root.state('zoomed')  # Start maximized on Windows
        self.root.minsize(1200, 800)  # Minimum window size
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Configure responsive styles
        self.configure_responsive_styles()
        
        # Initialize variables
        self.init_variables()
        
        # Create responsive main interface
        self.create_responsive_interface()
        
        # Bind resize events
        self.root.bind('<Configure>', self.on_window_resize)
        
    def configure_responsive_styles(self):
        """Configure modern responsive UI styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Define color scheme
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'white': '#ffffff'
        }
        
        # Configure custom styles
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 18, 'bold'), 
                           background=self.colors['primary'], 
                           foreground=self.colors['white'])
        
        self.style.configure('Heading.TLabel', 
                           font=('Segoe UI', 12, 'bold'), 
                           background=self.colors['secondary'], 
                           foreground=self.colors['white'])
        
        self.style.configure('Modern.TFrame', 
                           background=self.colors['secondary'], 
                           relief='flat', 
                           borderwidth=1)
        
        self.style.configure('Card.TFrame', 
                           background=self.colors['light'], 
                           relief='raised', 
                           borderwidth=2)
        
        # Configure notebook style
        self.style.configure('TNotebook', 
                           background=self.colors['primary'],
                           borderwidth=0)
        
        self.style.configure('TNotebook.Tab', 
                           background=self.colors['secondary'],
                           foreground=self.colors['white'],
                           padding=[20, 10],
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', self.colors['accent']),
                                ('active', self.colors['warning'])])
    
    def init_variables(self):
        """Initialize all tkinter variables"""
        # Rental variables
        self.AcctOpen = StringVar()
        self.AppDate = StringVar()
        self.NextCreditReview = StringVar()
        self.LastCreditReview = StringVar()
        self.DateRev = StringVar()
        self.ProdCode = StringVar()
        self.ProdType = StringVar()
        self.NoDays = StringVar()
        self.CostPDay = StringVar()
        self.CreLimit = StringVar()
        self.CreCheck = StringVar()
        self.SettDueDay = StringVar()
        self.PaymentD = StringVar()
        self.Discount = StringVar()
        self.Deposit = StringVar()
        self.PayDueDay = StringVar()
        self.PaymentM = StringVar()
        
        # Checkbox variables
        self.var1 = IntVar()  # Check Credit
        self.var2 = IntVar()  # Term Agreed
        self.var3 = IntVar()  # Account On Hold
        self.var4 = IntVar()  # Restrict Mailing
        
        # Calculation variables
        self.Tax = StringVar()
        self.SubTotal = StringVar()
        self.Total = StringVar()
        self.Receipt_Ref = StringVar()
        
        # Customer variables
        self.customer_id = StringVar()
        self.customer_name = StringVar()
        self.customer_phone = StringVar()
        self.customer_email = StringVar()
        self.customer_address = StringVar()

        # Product variables (NEW)
        self.product_id_var = StringVar()
        self.product_type_var = StringVar()
        self.product_code_var = StringVar()
        self.cost_per_day_var = StringVar()
        self.available_quantity_var = StringVar()
        self.product_status_var = StringVar()
        
        # Search variable
        self.search_var = StringVar()
    
    def create_responsive_interface(self):
        """Create responsive main interface"""
        # Main container with scrollable frame
        self.main_container = Frame(self.root, bg=self.colors['primary'])
        self.main_container.pack(fill=BOTH, expand=True)
        
        # Header
        self.create_header()
        
        # Notebook for tabs
        self.create_responsive_notebook()
    
    def create_header(self):
        """Create responsive header"""
        header_frame = Frame(self.main_container, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=X, padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = Label(header_frame, 
                          text="Rental Inventory Management System", 
                          font=('Segoe UI', 24, 'bold'), 
                          bg=self.colors['primary'], 
                          fg=self.colors['white'])
        title_label.pack(side=LEFT, pady=20)
        
        # Quick stats frame
        stats_frame = Frame(header_frame, bg=self.colors['primary'])
        stats_frame.pack(side=RIGHT, pady=20)
        
        self.create_quick_stats(stats_frame)
    
    def create_quick_stats(self, parent):
        """Create quick statistics display"""
        try:
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM rentals')
            total_rentals = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(total) FROM rentals')
            total_revenue = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Stats labels
            Label(parent, text=f"Total Rentals: {total_rentals}", 
                  font=('Segoe UI', 12, 'bold'), 
                  bg=self.colors['primary'], 
                  fg=self.colors['white']).pack(anchor=E)
            
            Label(parent, text=f"Total Revenue: £{total_revenue:.2f}", 
                  font=('Segoe UI', 12, 'bold'), 
                  bg=self.colors['primary'], 
                  fg=self.colors['white']).pack(anchor=E)
        
        except Exception as e:
            Label(parent, text="Stats unavailable", 
                  font=('Segoe UI', 12), 
                  bg=self.colors['primary'], 
                  fg=self.colors['white']).pack(anchor=E)
    
    def create_responsive_notebook(self):
        """Create responsive tabbed interface"""
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create tabs
        self.rental_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)
        self.customer_tab = ttk.Frame(self.notebook)
        self.product_tab = ttk.Frame(self.notebook) # NEW Product Tab
        
        self.notebook.add(self.rental_tab, text="  New Rental  ")
        self.notebook.add(self.history_tab, text="  Rental History  ")
        self.notebook.add(self.analytics_tab, text="  Analytics  ")
        self.notebook.add(self.customer_tab, text="  Customers  ")
        self.notebook.add(self.product_tab, text="  Products  ") # Add Product Tab
        
        # Setup each tab with responsive design
        self.setup_responsive_rental_tab()
        self.setup_responsive_history_tab()
        self.setup_responsive_analytics_tab()
        self.setup_responsive_customer_tab()
        self.setup_responsive_product_tab() # Setup Product Tab
        
    def setup_responsive_rental_tab(self):
        """Setup responsive rental tab"""
        # Create scrollable canvas
        canvas = Canvas(self.rental_tab, bg=self.colors['light'])
        scrollbar = ttk.Scrollbar(self.rental_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg=self.colors['light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main grid layout
        main_grid = Frame(scrollable_frame, bg=self.colors['light'])
        main_grid.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights for responsiveness
        main_grid.grid_columnconfigure(0, weight=1)
        main_grid.grid_columnconfigure(1, weight=1)
        main_grid.grid_rowconfigure(0, weight=0)
        main_grid.grid_rowconfigure(1, weight=0)
        main_grid.grid_rowconfigure(2, weight=1)
        
        # Customer Selection Section
        self.create_customer_selection_section(main_grid)
        
        # Product and Pricing Section
        self.create_product_section(main_grid)
        
        # Payment and Receipt Section
        self.create_payment_section(main_grid)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_customer_selection_section(self, parent):
        """Create customer selection section"""
        customer_frame = ttk.LabelFrame(parent, text="Customer Information", padding=15)
        customer_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Configure internal grid
        customer_frame.grid_columnconfigure(1, weight=1)
        customer_frame.grid_columnconfigure(3, weight=1)
        
        # Customer selection
        Label(customer_frame, text="Select Customer:", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_id, 
                                         font=('Segoe UI', 10), state='readonly', width=30)
        self.customer_combo.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        self.customer_combo.bind("<<ComboboxSelected>>", self.customer_selected)
        
        # Add customer button
        Button(customer_frame, text="Add New Customer", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['success'], fg=self.colors['white'],
               command=self.show_add_customer_dialog).grid(row=0, column=2, padx=10)
        
        # Customer details display
        self.customer_details_label = Label(customer_frame, text="No customer selected", 
                                          font=('Segoe UI', 10), fg=self.colors['secondary'])
        self.customer_details_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 0))
        
        self.load_customers()
    
    def create_product_section(self, parent):
        """Create responsive product section"""
        product_frame = ttk.LabelFrame(parent, text="Product & Rental Details", padding=15)
        product_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        # Configure grid
        for i in range(6):
            product_frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            product_frame.grid_columnconfigure(i, weight=1)
        
        # Product Type
        Label(product_frame, text="Product Type:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=5)
        self.cboProdType = ttk.Combobox(product_frame, textvariable=self.ProdType, state='readonly', 
                                       font=('Segoe UI', 10))
        self.cboProdType.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.cboProdType.bind("<<ComboboxSelected>>", self.product_selected)
        # Dynamically load product types
        self.load_product_types_for_rental()
        
        # Number of Days
        Label(product_frame, text="Rental Period:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.cboNoDays = ttk.Combobox(product_frame, textvariable=self.NoDays, state='readonly',
                                     font=('Segoe UI', 10))
        self.cboNoDays.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        self.cboNoDays.bind("<<ComboboxSelected>>", self.days_selected)
        self.cboNoDays['values'] = ('Select', '1-30 days', '31-90 days', '91-270 days', '271-365 days')
        self.cboNoDays.current(0)
        
        # Product Code
        Label(product_frame, text="Product Code:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=5)
        Entry(product_frame, textvariable=self.ProdCode, font=('Segoe UI', 10), state='readonly').grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Cost Per Day
        Label(product_frame, text="Daily Rate:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        Entry(product_frame, textvariable=self.CostPDay, font=('Segoe UI', 10), state='readonly').grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        
        # Payment Terms
        Label(product_frame, text="Credit Limit:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky="w", pady=5)
        self.cboCreLimit = ttk.Combobox(product_frame, textvariable=self.CreLimit, state='readonly', 
                                       font=('Segoe UI', 10))
        self.cboCreLimit.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.cboCreLimit['values'] = ('Select', '£150', '£200', '£250', '£300')
        self.cboCreLimit.current(0)
        
        Label(product_frame, text="Discount:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=2, sticky="w", pady=5)
        self.cboDiscount = ttk.Combobox(product_frame, textvariable=self.Discount, state='readonly', 
                                       font=('Segoe UI', 10))
        self.cboDiscount.grid(row=2, column=3, sticky="ew", padx=5, pady=5)
        self.cboDiscount['values'] = ('Select', '0%', '5%', '10%', '15%', '20%')
        self.cboDiscount.current(0)
        
        # Payment Method
        Label(product_frame, text="Payment Method:", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky="w", pady=5)
        self.cboPaymentM = ttk.Combobox(product_frame, textvariable=self.PaymentM, state='readonly',
                                       font=('Segoe UI', 10))
        self.cboPaymentM.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.cboPaymentM['values'] = ('Select', 'Cash', 'Visa Card', 'Master Card', 'Debit Card')
        self.cboPaymentM.current(0)
        
        # Additional checkboxes
        checkbox_frame = Frame(product_frame)
        checkbox_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        self.chk1 = Checkbutton(checkbox_frame, text="Credit Check Required", variable=self.var1, font=('Segoe UI', 9))
        self.chk1.pack(side=LEFT, padx=10)
        
        self.chk2 = Checkbutton(checkbox_frame, text="Terms Agreed", variable=self.var2, font=('Segoe UI', 9))
        self.chk2.pack(side=LEFT, padx=10)
        
        # Calculate button
        Button(product_frame, text="Calculate Total", font=('Segoe UI', 12, 'bold'),
               bg=self.colors['accent'], fg=self.colors['white'], 
               command=self.calculate_total).grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Save button
        Button(product_frame, text="Save Rental", font=('Segoe UI', 12, 'bold'),
               bg=self.colors['success'], fg=self.colors['white'], 
               command=self.save_rental).grid(row=5, column=2, columnspan=2, pady=10, sticky="ew", padx=(10, 0))
    
    def create_payment_section(self, parent):
        """Create payment and receipt section"""
        payment_frame = ttk.LabelFrame(parent, text="Billing & Receipt", padding=15)
        payment_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        
        # Configure grid
        payment_frame.grid_rowconfigure(1, weight=1)
        payment_frame.grid_columnconfigure(0, weight=1)
        
        # Billing summary
        billing_frame = Frame(payment_frame)
        billing_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        billing_frame.grid_columnconfigure(1, weight=1)
        
        Label(billing_frame, text="Subtotal:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=2)
        Entry(billing_frame, textvariable=self.SubTotal, font=('Segoe UI', 10), state='readonly').grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        Label(billing_frame, text="Tax (15%):", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=2)
        Entry(billing_frame, textvariable=self.Tax, font=('Segoe UI', 10), state='readonly').grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        Label(billing_frame, text="Total:", font=('Segoe UI', 12, 'bold')).grid(row=2, column=0, sticky="w", pady=5)
        Entry(billing_frame, textvariable=self.Total, font=('Segoe UI', 12, 'bold'), state='readonly').grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Receipt display
        receipt_label = Label(payment_frame, text="Receipt Preview:", font=('Segoe UI', 10, 'bold'))
        receipt_label.grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        self.txtReceipt = Text(payment_frame, font=('Consolas', 9), wrap=WORD, height=20)
        receipt_scroll = ttk.Scrollbar(payment_frame, orient=VERTICAL, command=self.txtReceipt.yview)
        self.txtReceipt.configure(yscrollcommand=receipt_scroll.set)
        
        receipt_container = Frame(payment_frame)
        receipt_container.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        receipt_container.grid_rowconfigure(0, weight=1)
        receipt_container.grid_columnconfigure(0, weight=1)
        
        self.txtReceipt.grid(row=0, column=0, sticky="nsew", in_=receipt_container)
        receipt_scroll.grid(row=0, column=1, sticky="ns", in_=receipt_container)
        
        # Action buttons
        button_frame = Frame(payment_frame)
        button_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        Button(button_frame, text="Print Receipt", font=('Segoe UI', 10),
               bg=self.colors['secondary'], fg=self.colors['white'],
               command=self.print_receipt).pack(side=LEFT, padx=(0, 10))
        
        Button(button_frame, text="Reset Form", font=('Segoe UI', 10),
               bg=self.colors['warning'], fg=self.colors['white'],
               command=self.reset_form).pack(side=LEFT)
    
    def setup_responsive_history_tab(self):
        """Setup responsive history tab"""
        history_main = Frame(self.history_tab, bg=self.colors['light'])
        history_main.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Search and filter section
        search_frame = ttk.LabelFrame(history_main, text="Search & Filter", padding=15)
        search_frame.pack(fill=X, pady=(0, 20))
        
        search_frame.grid_columnconfigure(1, weight=1)
        
        Label(search_frame, text="Search:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        search_entry = Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 10))
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        search_entry.bind('<KeyRelease>', lambda e: self.search_rentals())
        
        Button(search_frame, text="Search", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['accent'], fg=self.colors['white'],
               command=self.search_rentals).grid(row=0, column=2, padx=5)
        
        Button(search_frame, text="Show All", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['success'], fg=self.colors['white'],
               command=self.load_all_rentals).grid(row=0, column=3, padx=5)
        
        Button(search_frame, text="Export PDF", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['danger'], fg=self.colors['white'],
               command=self.export_to_pdf).grid(row=0, column=4, padx=5)
        
        # History treeview
        tree_frame = Frame(history_main)
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Configure treeview with better columns
        columns = ('ID', 'Receipt', 'Customer', 'Product', 'Days', 'Total', 'Date')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Define headings and column widths
        column_widths = {'ID': 80, 'Receipt': 150, 'Customer': 150, 'Product': 120, 'Days': 80, 'Total': 100, 'Date': 150}
        
        for col in columns:
            self.history_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.history_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.history_tree.xview)
        
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Load initial data
        self.load_all_rentals()
    
    def setup_responsive_analytics_tab(self):
        """Setup responsive analytics tab"""
        analytics_main = Frame(self.analytics_tab, bg=self.colors['light'])
        analytics_main.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Control panel
        control_frame = ttk.LabelFrame(analytics_main, text="Analytics Controls", padding=15)
        control_frame.pack(fill=X, pady=(0, 20))
        
        Button(control_frame, text="Product Distribution", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['accent'], fg=self.colors['white'],
               command=self.show_product_distribution).pack(side=LEFT, padx=(0, 10))
        
        Button(control_frame, text="Monthly Revenue", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['success'], fg=self.colors['white'],
               command=self.show_monthly_revenue).pack(side=LEFT, padx=(0, 10))
        
        Button(control_frame, text="Customer Statistics", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['warning'], fg=self.colors['white'],
               command=self.show_customer_stats).pack(side=LEFT, padx=(0, 10))
        
        Button(control_frame, text="Refresh Charts", font=('Segoe UI', 10, 'bold'),
               bg=self.colors['secondary'], fg=self.colors['white'],
               command=self.refresh_charts).pack(side=RIGHT)
        
        # Chart area
        chart_frame = Frame(analytics_main, bg=self.colors['white'], relief='raised', bd=2)
        chart_frame.pack(fill=BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), facecolor=self.colors['white'])
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Initialize with default chart
        self.show_product_distribution()
    
    def setup_responsive_customer_tab(self):
        """Setup responsive customer management tab"""
        customer_main = Frame(self.customer_tab, bg=self.colors['light'])
        customer_main.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Customer form
        form_frame = ttk.LabelFrame(customer_main, text="Customer Management", padding=15)
        form_frame.pack(fill=X, pady=(0, 20))
        
        # Configure grid
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        
        # Form fields
        Label(form_frame, text="Full Name:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.customer_name, font=('Segoe UI', 10)).grid(row=0, column=1, sticky="ew", padx=(10, 20), pady=5)
        
        Label(form_frame, text="Phone:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.customer_phone, font=('Segoe UI', 10)).grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        Label(form_frame, text="Email:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.customer_email, font=('Segoe UI', 10)).grid(row=1, column=1, sticky="ew", padx=(10, 20), pady=5)
        
        Label(form_frame, text="Address:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=2, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.customer_address, font=('Segoe UI', 10)).grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        Button(button_frame, text="Add Customer", font=('Segoe UI', 11, 'bold'),
               bg=self.colors['success'], fg=self.colors['white'],
               command=self.add_customer).pack(side=LEFT, padx=(0, 10))
        
        Button(button_frame, text="Update Customer", font=('Segoe UI', 11, 'bold'),
               bg=self.colors['accent'], fg=self.colors['white'],
               command=self.update_customer).pack(side=LEFT, padx=(0, 10))
        
        Button(button_frame, text="Clear Form", font=('Segoe UI', 11, 'bold'),
               bg=self.colors['warning'], fg=self.colors['white'],
               command=self.clear_customer_form).pack(side=LEFT)
        
        # Customer list
        list_frame = ttk.LabelFrame(customer_main, text="Customer Directory", padding=15)
        list_frame.pack(fill=BOTH, expand=True)
        
        # Customer treeview
        cust_tree_frame = Frame(list_frame)
        cust_tree_frame.pack(fill=BOTH, expand=True)
        
        cust_columns = ('ID', 'Name', 'Phone', 'Email', 'Address', 'Created')
        self.customer_tree = ttk.Treeview(cust_tree_frame, columns=cust_columns, show='headings', height=15)
        
        # Define customer tree headings
        cust_col_widths = {'ID': 60, 'Name': 150, 'Phone': 120, 'Email': 180, 'Address': 200, 'Created': 100}
        
        for col in cust_columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=cust_col_widths.get(col, 100))
        
        # Customer tree scrollbars
        cust_v_scroll = ttk.Scrollbar(cust_tree_frame, orient=VERTICAL, command=self.customer_tree.yview)
        cust_h_scroll = ttk.Scrollbar(cust_tree_frame, orient=HORIZONTAL, command=self.customer_tree.xview)
        
        self.customer_tree.configure(yscrollcommand=cust_v_scroll.set, xscrollcommand=cust_h_scroll.set)
        
        # Pack customer tree
        self.customer_tree.grid(row=0, column=0, sticky="nsew")
        cust_v_scroll.grid(row=0, column=1, sticky="ns")
        cust_h_scroll.grid(row=1, column=0, sticky="ew")
        
        cust_tree_frame.grid_rowconfigure(0, weight=1)
        cust_tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        
        # Load customers
        self.load_customers_tree()
    
    def setup_responsive_product_tab(self): # NEW Product Tab Setup
        """Setup responsive product management tab"""
        product_main = Frame(self.product_tab, bg=self.colors['light'])
        product_main.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Product form
        form_frame = ttk.LabelFrame(product_main, text="Product Details", padding=15)
        form_frame.pack(fill=X, pady=(0, 20))
        
        # Configure grid
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        
        # Form fields
        Label(form_frame, text="Product Type:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.product_type_var, font=('Segoe UI', 10)).grid(row=0, column=1, sticky="ew", padx=(10, 20), pady=5)
        
        Label(form_frame, text="Product Code:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.product_code_var, font=('Segoe UI', 10)).grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        Label(form_frame, text="Cost Per Day:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.cost_per_day_var, font=('Segoe UI', 10)).grid(row=1, column=1, sticky="ew", padx=(10, 20), pady=5)
        
        Label(form_frame, text="Available Quantity:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=2, sticky="w", pady=5)
        Entry(form_frame, textvariable=self.available_quantity_var, font=('Segoe UI', 10)).grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)

        Label(form_frame, text="Status:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky="w", pady=5)
        ttk.Combobox(form_frame, textvariable=self.product_status_var, values=['Available', 'Unavailable', 'Maintenance'], state='readonly', font=('Segoe UI', 10)).grid(row=2, column=1, sticky="ew", padx=(10, 20), pady=5)
        
        # Buttons
        button_frame = Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        Button(button_frame, text="Add Product", font=('Segoe UI', 11, 'bold'),
               bg=self.colors['success'], fg=self.colors['white'],
               command=self.add_product_to_db).pack(side=LEFT, padx=(0, 10))
        
        Button(button_frame, text="Update Product", font=('Segoe UI', 11, 'bold'),
               bg=self.colors['accent'], fg=self.colors['white'],
               command=self.update_product_in_db).pack(side=LEFT, padx=(0, 10))
        
        Button(button_frame, text="Delete Product", font=('Segoe UI', 11, 'bold'),
               bg=self.colors['danger'], fg=self.colors['white'],
               command=self.delete_product_from_db).pack(side=LEFT, padx=(0, 10))

        Button(button_frame, text="Clear Form", font=('Segoe UI', 11, 'bold'),
               bg=self.colors['warning'], fg=self.colors['white'],
               command=self.clear_product_form).pack(side=LEFT)
        
        # Product list
        list_frame = ttk.LabelFrame(product_main, text="Product Inventory", padding=15)
        list_frame.pack(fill=BOTH, expand=True)
        
        # Product treeview
        prod_tree_frame = Frame(list_frame)
        prod_tree_frame.pack(fill=BOTH, expand=True)
        
        prod_columns = ('ID', 'Type', 'Code', 'Cost/Day', 'Quantity', 'Status')
        self.product_tree = ttk.Treeview(prod_tree_frame, columns=prod_columns, show='headings', height=15)
        
        # Define product tree headings
        prod_col_widths = {'ID': 60, 'Type': 120, 'Code': 100, 'Cost/Day': 100, 'Quantity': 80, 'Status': 100}
        
        for col in prod_columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=prod_col_widths.get(col, 100))
        
        # Product tree scrollbars
        prod_v_scroll = ttk.Scrollbar(prod_tree_frame, orient=VERTICAL, command=self.product_tree.yview)
        prod_h_scroll = ttk.Scrollbar(prod_tree_frame, orient=HORIZONTAL, command=self.product_tree.xview)
        
        self.product_tree.configure(yscrollcommand=prod_v_scroll.set, xscrollcommand=prod_h_scroll.set)
        
        # Pack product tree
        self.product_tree.grid(row=0, column=0, sticky="nsew")
        prod_v_scroll.grid(row=0, column=1, sticky="ns")
        prod_h_scroll.grid(row=1, column=0, sticky="ew")
        
        prod_tree_frame.grid_rowconfigure(0, weight=1)
        prod_tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.product_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        
        # Load products
        self.load_products_tree()
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Update quick stats when window resizes
            pass
    
    def load_customers(self):
        """Load customers into combobox"""
        try:
            customers = self.db_manager.get_all_customers()
            customer_list = ["Select Customer"]
            self.customer_dict = {}
            
            for customer in customers:
                display_name = f"{customer[1]} (ID: {customer[0]})"
                customer_list.append(display_name)
                self.customer_dict[display_name] = {
                    'id': customer[0],
                    'name': customer[1],
                    'phone': customer[2] or '',
                    'email': customer[3] or '',
                    'address': customer[4] or ''
                }
            
            self.customer_combo['values'] = customer_list
            self.customer_combo.current(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def customer_selected(self, event):
        """Handle customer selection"""
        selected = self.customer_combo.get()
        if selected in self.customer_dict:
            customer = self.customer_dict[selected]
            self.customer_details_label.config(
                text=f"Selected: {customer['name']} | Phone: {customer['phone']} | Email: {customer['email']}"
            )
        else:
            self.customer_details_label.config(text="No customer selected")
    
    def show_add_customer_dialog(self):
        """Show add customer dialog"""
        self.notebook.select(self.customer_tab)
        self.customer_name.focus()
    
    def load_product_types_for_rental(self):
        """Load available product types into the rental tab combobox."""
        try:
            products = self.db_manager.get_all_products()
            product_types = sorted(list(set([p[1] for p in products if p[4] > 0 and p[5] == 'Available']))) # Only available products
            
            self.cboProdType['values'] = ['Select'] + product_types
            self.cboProdType.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product types: {str(e)}")
    
    def product_selected(self, event):
        """Handle product type selection with improved logic"""
        product_type = self.cboProdType.get()
        
        # Fetch product details from DB based on selected type
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT product_code, cost_per_day FROM products WHERE product_type = ? AND available_quantity > 0 AND status = "Available" LIMIT 1', (product_type,))
        product_info = cursor.fetchone()
        conn.close()

        if product_info:
            self.ProdCode.set(product_info[0])
            self.CostPDay.set(f"£{product_info[1]:.2f}")
            
            # Set reasonable defaults
            self.CreCheck.set("No")
            self.PaymentD.set("No")
            self.Deposit.set("No")
            
            # Auto-calculate if days are selected
            self.auto_calculate_dates()
        else:
            self.ProdCode.set("")
            self.CostPDay.set("")
            messagebox.showwarning("No Product", f"No available product found for type: {product_type}")
    
    def days_selected(self, event):
        """Handle rental period selection"""
        period = self.cboNoDays.get()
        
        period_configs = {
            "1-30 days": {"days": 30, "limit": "£150", "discount": "5%"},
            "31-90 days": {"days": 90, "limit": "£200", "discount": "10%"},
            "91-270 days": {"days": 270, "limit": "£250", "discount": "15%"},
            "271-365 days": {"days": 365, "limit": "£300", "discount": "20%"}
        }
        
        if period in period_configs:
            config = period_configs[period]
            
            # Set dates
            today = datetime.date.today()
            end_date = today + datetime.timedelta(days=config["days"])
            
            self.AppDate.set(str(today))
            self.NextCreditReview.set(str(end_date))
            self.LastCreditReview.set(str(config["days"]))
            self.DateRev.set(str(end_date))
            
            # Set credit and discount
            self.CreLimit.set(config["limit"])
            self.Discount.set(config["discount"])
            self.AcctOpen.set("Yes")
            
            # Auto-calculate total if product is selected
            self.auto_calculate_dates()
    


if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = ImprovedRentalInventory(root)
        
        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (root.winfo_screenheight() // 2) - (900 // 2)
        root.geometry(f"1400x900+{x}+{y}")
        
        root.mainloop()
        
    except Exception as e:
        import tkinter.messagebox as msg
        msg.showerror("Application Error", f"Failed to start application:\n{str(e)}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()