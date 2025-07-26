import pandas as pd
from sqlalchemy import create_engine
from models import Base, Product, Order
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Connect to PostgreSQL using DB_URL from .env
engine = create_engine(os.getenv("DB_URL"))

# Create tables if not already created
Base.metadata.create_all(engine)

# Load and insert product data from CSV
def load_products():
    df = pd.read_csv("products.csv")
    df.to_sql("products", engine, if_exists="replace", index=False)

# Load and insert order data from CSV
def load_orders():
    df = pd.read_csv("orders.csv")
    df.to_sql("orders", engine, if_exists="replace", index=False)

# Run both loaders
load_products()
load_orders()