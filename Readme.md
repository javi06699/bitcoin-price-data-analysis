# Finance Data Project

This project focuses on downloading, storing, and analyzing financial data for **Bitcoin (BTC-USD)** .
The workflow is divided into multiple scripts, each with a specific role: **data extraction, database storage, ETL/analysis, and forecasting**.  

The main idea behind this project is to move away from raw CSV files and instead use a **database (PostgreSQL)**.  
Why? Because databases allow:
- Better **data integrity** (no risk of modifying CSVs accidentally).
- Easier **scalability** when more assets are added.
- Efficient **querying** for analysis, filtering, or aggregation.
- A more **professional and reproducible workflow**.

---

## Project Workflow

### 1. `download_data.py`
- Downloads historical data for BTC and S&P500 using the `yfinance` library.  
- Saves the data as CSV files (`btc_data.csv` ) with custom headers.

👉 **Why not stop here?**  
While CSVs are fine for small projects, they are not ideal for scaling or serious analysis.  
Databases ensure structured storage, consistency, and efficiency for future queries.

---

### 2. `load_postgres.py`
- Loads the CSV files into a **PostgreSQL database**.
- Ensures that all column names are lowercase for consistency.
- Adds an `asset_id` field to distinguish between BTC (1) and additional stocks.
- Appends the data into a unified table called `prices`.

👉 **Why use PostgreSQL?**
- Databases allow combining multiple assets in one table with clear identifiers.
- They handle large datasets more efficiently than flat files.
- Future analyses (like joining with macroeconomic indicators) become much easier.

---

### 3. `analysis_etl.py`
- Connects to the database on PostgreSQL.  
- Performs **ETL (Extract, Transform, Load)**:
  - Cleans and preprocesses the financial data.
  - Creates additional fields such as year, month, and year-month.
- Performs **analysis**:
  - Calculates monthly returns and average seasonal patterns.
  - Visualizes results with bar charts and heatmaps.
  - Computes the **realized price** (volume-weighted metric).
  - Computes the **Short-Therm-Holders realized price**.
  - Computes the **Long-Therm-Holders realized price**.
- Performs **forecasting**:
  - Uses **Facebook Prophet** to forecast future price movements with uncertainty intervals.

👉 **Why not analyze directly from CSVs?**
- Using a database allows you to easily extend the project to multiple assets without rewriting CSV-handling logic.
- Queries are more flexible (e.g., "give me BTC returns after 2018 only").
- Ensures a **repeatable pipeline**: raw data → database → ETL → analysis.

---

## How to Run the Project

### 1. Install dependencies
```bash
pip install -r requirements.txt
python scripts/download_data.py
python scripts/load_postgres.py
python scripts/analysis_etl.py

