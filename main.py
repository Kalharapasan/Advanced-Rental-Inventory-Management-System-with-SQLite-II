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
