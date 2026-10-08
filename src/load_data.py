import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = "localhost"  # Connecting to Docker container from host PC
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "ecommerce_db")

# Construct PostgreSQL connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Mapping table names to exact processed file paths (in Foreign Key order)
TABLE_FILE_MAP = [
    ("sellers", "data/processed/olist_sellers_dataset.csv"),
    ("customers", "data/processed/olist_customers_dataset.csv"),
    ("geolocation", "data/processed/olist_geolocation_dataset.csv"),
    ("product_category_name_translation", "data/processed/product_category_name_translation.csv"),
    ("products", "data/processed/olist_products_dataset.csv"),
    ("orders", "data/processed/olist_orders_dataset.csv"),
    ("order_items", "data/processed/olist_order_items_dataset.csv"),
    ("order_payments", "data/processed/olist_order_payments_dataset.csv"),
    ("order_reviews", "data/processed/olist_order_reviews_dataset.csv"),
]

def load_data_to_postgres():
    print("Loading processed CSV data into PostgreSQL...")
    
    with engine.connect() as conn:
        for table_name, file_path in TABLE_FILE_MAP:
            if os.path.exists(file_path):
                print(f"Loading {file_path} -> Table: '{table_name}'...")
                df = pd.read_csv(file_path)
                
                # Convert string columns ending with '_timestamp', '_date', or '_at' to datetime
                datetime_cols = [col for col in df.columns if col.endswith(('_timestamp', '_date', '_at'))]
                for col in datetime_cols:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Append processed data into target table
                df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
                print(f"Successfully inserted {len(df)} rows into '{table_name}'.")
            else:
                print(f"File not found: {file_path}")

    print("\nETL Data Pipeline Completed Successfully!")

if __name__ == "__main__":
    load_data_to_postgres()