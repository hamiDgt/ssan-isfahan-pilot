import pandas as pd
from sqlalchemy import create_engine

df = pd.read_parquet('/home/hmid/ssan-data/reliability_cells.parquet')
engine = create_engine('postgresql+psycopg2://ssan:password123@localhost:5432/ssan_db')
df.to_sql('reliability_cells', engine, if_exists='replace', index=False)
print("Exported reliability cells to SQL.")
