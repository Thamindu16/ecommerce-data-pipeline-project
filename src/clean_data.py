import os
import pandas as pd

# Define relative paths
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"


def ensure_directories():
    """Ensure the processed directory exists."""
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)


def clean_geolocation(raw_path):
    """Clean geolocation dataset by removing duplicate zip codes."""
    df = pd.read_csv(os.path.join(raw_path, "olist_geolocation_dataset.csv"))

    # Group by zip code prefix and take the average latitude and longitude
    df_cleaned = (
        df.groupby("geolocation_zip_code_prefix")
        .agg(
            {
                "geolocation_lat": "mean",
                "geolocation_lng": "mean",
                "geolocation_city": "first",
                "geolocation_state": "first",
            }
        )
        .reset_index()
    )

    return df_cleaned


def clean_orders(raw_path):
    """Clean orders dataset by converting timestamp columns to datetime objects."""
    df = pd.read_csv(os.path.join(raw_path, "olist_orders_dataset.csv"))

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def clean_products(raw_path):
    """Clean products dataset by filling missing values in categorical fields."""
    df = pd.read_csv(os.path.join(raw_path, "olist_products_dataset.csv"))

    # Impute missing product category names with 'unknown'
    df["product_category_name"] = df["product_category_name"].fillna("unknown")

    # Fill numerical measurements with median values
    num_cols = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())

    return df


def run_data_cleaning_pipeline():
    """Execute full data cleaning workflow for all datasets."""
    print("Starting Data Cleaning Pipeline...\n")
    ensure_directories()

    # List of files to process directly without custom rules
    standard_files = [
        "olist_customers_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_order_reviews_dataset.csv",
        "olist_sellers_dataset.csv",
        "product_category_name_translation.csv",
    ]

    # Process standard files (Remove exact row duplicates if any)
    for file_name in standard_files:
        df = pd.read_csv(os.path.join(RAW_DATA_PATH, file_name))
        initial_len = len(df)
        df_cleaned = df.drop_duplicates()
        save_path = os.path.join(PROCESSED_DATA_PATH, file_name)
        df_cleaned.to_csv(save_path, index=False)
        print(
            f"Processed: {file_name} | Rows: {len(df_cleaned):,} (Dropped {initial_len - len(df_cleaned)} duplicates)"
        )

    # Process geolocation dataset with deduplication
    geo_df = clean_geolocation(RAW_DATA_PATH)
    geo_df.to_csv(
        os.path.join(PROCESSED_DATA_PATH, "olist_geolocation_dataset.csv"),
        index=False,
    )
    print(
        f"Processed: olist_geolocation_dataset.csv | Rows reduced to: {len(geo_df):,}"
    )

    # Process orders dataset with datetime conversions
    orders_df = clean_orders(RAW_DATA_PATH)
    orders_df.to_csv(
        os.path.join(PROCESSED_DATA_PATH, "olist_orders_dataset.csv"),
        index=False,
    )
    print(f"Processed: olist_orders_dataset.csv | Rows: {len(orders_df):,}")

    # Process products dataset with imputed missing values
    products_df = clean_products(RAW_DATA_PATH)
    products_df.to_csv(
        os.path.join(PROCESSED_DATA_PATH, "olist_products_dataset.csv"),
        index=False,
    )
    print(
        f"Processed: olist_products_dataset.csv | Rows: {len(products_df):,}"
    )

    print("\nData Cleaning Pipeline Completed Successfully!")


if __name__ == "__main__":
    run_data_cleaning_pipeline()