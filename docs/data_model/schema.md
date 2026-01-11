# Analytical Data Model

This document defines the analytical data model used to evaluate the performance of physical branches versus digital channels in a retail banking context.

The model follows a star-schema approach, separating dimensions (context) from fact tables (events and measures), and is designed to support executive reporting, profitability analysis, and customer behavior insights.

---

## Dimensions

### dim_customer

**Grain:** One row per customer

**Primary Key:** customer_id

**Description:**  
Represents the master record for retail banking customers, including onboarding channel, segment, and regional context.

**Key Columns:**
- customer_id
- onboarding_date
- onboarding_channel (branch, digital)
- primary_branch_id (nullable for digital customers)
- customer_segment (mass, affluent, SME)
- region
- is_active

**Relationships:**
- One-to-many with fact_account
- One-to-many with fact_monthly_customer_metrics

---

### dim_branch

**Grain:** One row per branch

**Primary Key:** branch_id

**Description:**  
Represents physical bank branches and their operational characteristics.

**Key Columns:**
- branch_id
- region
- branch_type (urban, suburban, rural)
- opening_date
- monthly_operating_cost

**Relationships:**
- One-to-many with dim_customer
- One-to-many with fact_transaction

---

### dim_product

**Grain:** One row per banking product

**Primary Key:** product_id

**Description:**  
Defines retail banking products and their revenue characteristics.

**Key Columns:**
- product_id
- product_type (checking, savings, loan, credit)
- interest_rate
- monthly_fee
- revenue_type (interest, fee)

**Relationships:**
- One-to-many with fact_account

---

### dim_date

**Grain:** One row per calendar day

**Primary Key:** date_id

**Description:**  
Standard date dimension to support time-based analysis.

**Key Columns:**
- date_id
- calendar_date
- year
- month
- year_month
- day_of_week

**Relationships:**
- One-to-many with fact_transaction
- One-to-many with fact_monthly_customer_metrics

---

## Fact Tables

### fact_account

**Grain:** One row per account

**Primary Key:** account_id

**Description:**  
Represents customer financial accounts and their balances.

**Key Columns:**
- account_id
- customer_id
- product_id
- open_date
- close_date (nullable)
- avg_daily_balance

**Relationships:**
- Many-to-one with dim_customer
- Many-to-one with dim_product

---

### fact_transaction

**Grain:** One row per transaction

**Primary Key:** transaction_id

**Description:**  
Represents individual financial transactions executed by customers.

**Key Columns:**
- transaction_id
- account_id
- transaction_date
- transaction_type (deposit, withdrawal, payment)
- transaction_channel (branch, digital, ATM)
- transaction_amount

**Relationships:**
- Many-to-one with fact_account
- Many-to-one with dim_date
- Many-to-one with dim_branch (nullable for digital transactions)

---

### fact_monthly_customer_metrics

**Grain:** One row per customer per month

**Primary Key:** customer_id + year_month

**Description:**  
Pre-aggregated monthly metrics used for performance analysis and executive reporting.

**Key Columns:**
- customer_id
- year_month
- total_balance
- transaction_count
- digital_transaction_ratio
- estimated_revenue
- active_flag

**Relationships:**
- Many-to-one with dim_customer
- Many-to-one with dim_date

---

## Notes

- This model is optimized for analytical workloads and executive dashboards.
- Pre-aggregated tables are used to improve query performance and simplify KPI calculations.
- All revenue and cost metrics are derived using documented business assumptions.
