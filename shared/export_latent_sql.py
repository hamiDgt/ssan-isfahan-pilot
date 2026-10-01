import pandas as pd
from sqlalchemy import create_engine

df = pd.read_parquet('/home/hmid/ssan-data/latent_vectors.parquet')
engine = create_engine('postgresql+psycopg2://ssan:password123@localhost:5432/ssan_db')
df.to_sql('latent_vectors', engine, if_exists='replace', index=False)
print("Exported latent vectors to SQL.")
