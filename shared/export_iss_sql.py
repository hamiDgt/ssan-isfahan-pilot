import pandas as pd
from sqlalchemy import create_engine

df = pd.read_parquet('/home/hmid/ssan-data/iss_cells_d6.parquet')
engine = create_engine('postgresql+psycopg2://ssan:password123@localhost:5432/ssan_db')
df.to_sql('iss_cells', engine, if_exists='replace', index=False)
print("Exported ISS cells to SQL.")
