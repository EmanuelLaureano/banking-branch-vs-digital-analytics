import pandas as pd

# Load data
customers = pd.read_csv("data/raw/dim_customer.csv")
accounts = pd.read_csv("data/raw/fact_account.csv")
transactions = pd.read_csv("data/raw/fact_transaction.csv", parse_dates=["transaction_date"])
products = pd.read_csv("data/raw/dim_product.csv")

# Add year-month
transactions["year_month"] = transactions["transaction_date"].dt.to_period("M").astype(str)

# -----------------------------
# Transaction aggregation
# -----------------------------
tx_agg = (
    transactions
    .merge(accounts, on="account_id")
    .groupby(["customer_id", "year_month"])
    .agg(
        total_transactions=("transaction_id", "count"),
        total_volume=("transaction_amount", "sum"),
        avg_transaction_amount=("transaction_amount", "mean")
    )
    .reset_index()
)

# -----------------------------
# Revenue estimation
# -----------------------------
accounts_products = accounts.merge(products, on="product_id")

accounts_products["monthly_interest_revenue"] = (
    accounts_products["avg_daily_balance"] *
    accounts_products["interest_rate"] / 12
)

accounts_products["monthly_fee_revenue"] = accounts_products["monthly_fee"]

rev_agg = (
    accounts_products
    .groupby("customer_id")
    .agg(
        estimated_interest_revenue=("monthly_interest_revenue", "sum"),
        estimated_fee_revenue=("monthly_fee_revenue", "sum")
    )
    .reset_index()
)

# -----------------------------
# Final mart
# -----------------------------
monthly_metrics = (
    tx_agg
    .merge(rev_agg, on="customer_id", how="left")
    .merge(customers[["customer_id", "customer_segment", "onboarding_channel"]], on="customer_id")
)

monthly_metrics["customer_activity_flag"] = monthly_metrics["total_transactions"] > 0

# Export
monthly_metrics.to_csv(
    "data/analytics/fact_monthly_customer_metrics.csv",
    index=False
)

print("Monthly customer metrics built successfully.")
