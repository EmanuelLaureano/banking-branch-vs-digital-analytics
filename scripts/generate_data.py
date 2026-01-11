import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)

# -----------------------------
# Parameters
# -----------------------------
N_CUSTOMERS = 10_000
N_BRANCHES = 25
N_PRODUCTS = 6
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

# -----------------------------
# dim_branch
# -----------------------------
branches = pd.DataFrame({
    "branch_id": range(1, N_BRANCHES + 1),
    "region": np.random.choice(["North", "South", "East", "West"], N_BRANCHES),
    "branch_type": np.random.choice(["urban", "suburban", "rural"], N_BRANCHES, p=[0.5, 0.3, 0.2]),
    "opening_date": [fake.date_between(start_date="-20y", end_date="-5y") for _ in range(N_BRANCHES)],
    "monthly_operating_cost": np.random.normal(120_000, 25_000, N_BRANCHES).round(2)
})

# -----------------------------
# dim_product
# -----------------------------
products = pd.DataFrame({
    "product_id": range(1, N_PRODUCTS + 1),
    "product_type": ["checking", "savings", "credit_card", "personal_loan", "mortgage", "investment"],
    "interest_rate": [0.00, 0.02, 0.18, 0.12, 0.06, 0.05],
    "monthly_fee": [10, 0, 15, 0, 0, 25],
    "revenue_type": ["fee", "interest", "interest", "interest", "interest", "fee"]
})

# -----------------------------
# dim_customer
# -----------------------------
customers = pd.DataFrame({
    "customer_id": range(1, N_CUSTOMERS + 1),
    "onboarding_date": [fake.date_between(start_date="-5y", end_date="today") for _ in range(N_CUSTOMERS)],
    "onboarding_channel": np.random.choice(["branch", "digital"], N_CUSTOMERS, p=[0.6, 0.4]),
    "customer_segment": np.random.choice(["mass", "affluent", "SME"], N_CUSTOMERS, p=[0.7, 0.2, 0.1]),
    "region": np.random.choice(["North", "South", "East", "West"], N_CUSTOMERS),
    "is_active": np.random.choice([True, False], N_CUSTOMERS, p=[0.9, 0.1])
})

customers["primary_branch_id"] = np.where(
    customers["onboarding_channel"] == "branch",
    np.random.choice(branches["branch_id"], N_CUSTOMERS),
    np.nan
)

# -----------------------------
# fact_account
# -----------------------------
accounts = customers.sample(frac=1.3, replace=True).reset_index(drop=True)
accounts["account_id"] = range(1, len(accounts) + 1)
accounts["product_id"] = np.random.choice(products["product_id"], len(accounts))
accounts["open_date"] = accounts["onboarding_date"]
accounts["close_date"] = np.where(
    np.random.rand(len(accounts)) < 0.1,
    accounts["open_date"] + pd.to_timedelta(np.random.randint(90, 900, len(accounts)), unit="D"),
    pd.NaT
)
accounts["avg_daily_balance"] = np.random.lognormal(mean=9, sigma=1, size=len(accounts)).round(2)

accounts = accounts[[
    "account_id", "customer_id", "product_id",
    "open_date", "close_date", "avg_daily_balance"
]]

# -----------------------------
# dim_date
# -----------------------------
dates = pd.date_range(start=START_DATE, end=END_DATE)
dim_date = pd.DataFrame({
    "date_id": dates.strftime("%Y%m%d").astype(int),
    "calendar_date": dates,
    "year": dates.year,
    "month": dates.month,
    "year_month": dates.strftime("%Y-%m")
})

# -----------------------------
# fact_transaction
# -----------------------------
transactions = []
for _, acc in accounts.iterrows():
    n_tx = np.random.poisson(80)
    tx_dates = np.random.choice(dates, n_tx)
    for d in tx_dates:
        transactions.append({
            "transaction_id": len(transactions) + 1,
            "account_id": acc["account_id"],
            "transaction_date": d,
            "transaction_type": np.random.choice(["deposit", "withdrawal", "payment"]),
            "transaction_channel": np.random.choice(["branch", "digital", "ATM"], p=[0.25, 0.6, 0.15]),
            "transaction_amount": round(np.random.exponential(120), 2)
        })

fact_transaction = pd.DataFrame(transactions)

# -----------------------------
# Export
# -----------------------------
branches.to_csv("data/raw/dim_branch.csv", index=False)
products.to_csv("data/raw/dim_product.csv", index=False)
customers.to_csv("data/raw/dim_customer.csv", index=False)
accounts.to_csv("data/raw/fact_account.csv", index=False)
dim_date.to_csv("data/raw/dim_date.csv", index=False)
fact_transaction.to_csv("data/raw/fact_transaction.csv", index=False)

print("Synthetic data generated successfully.")
