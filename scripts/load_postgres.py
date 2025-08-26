from sqlalchemy import create_engine, text
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# conection to the database
ENGINE = create_engine("postgresql://postgres:*******@localhost:5432/finance_data")

def load_with_asset_id(csv_path, asset_id):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.lower()
    df['asset_id'] = asset_id
    return df

if __name__ == "__main__":
    btc_df = load_with_asset_id(DATA_DIR / "btc_data.csv", 1)
    #sp_df  = load_with_asset_id(DATA_DIR / "sp500_data.csv", 2)

    # Create empty table if not exists
    with ENGINE.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS prices;"))
        #let's create the table with the appropriate schema
        pass

    # load data
    btc_df.to_sql("prices", ENGINE, if_exists="replace", index=False)
    #sp_df.to_sql("prices", ENGINE, if_exists="append", index=False)
