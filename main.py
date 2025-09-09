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