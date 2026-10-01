import pandas as pd
from sqlalchemy import create_engine

df = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
df = df.rename(columns={'final_id':'h3','support':'iss','gss_context':'gss','center_lat':'lat','center_lon':'lon'})
engine = create_engine('postgresql+psycopg2://ssan:password123@localhost:5432/ssan_db')
df.to_sql('capsules', engine, if_exists='replace', index=False)
print("Exported D6 capsules to SQL.")
