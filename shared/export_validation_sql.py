import pandas as pd
from sqlalchemy import create_engine

df = pd.read_parquet('/home/hmid/ssan-data/validation_report.parquet')
engine = create_engine('postgresql+psycopg2://ssan:password123@localhost:5432/ssan_db')
df.to_sql('validation_report', engine, if_exists='replace', index=False)
print("Exported validation report to SQL.")
