import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.pipeline import pipeline

edges_df = pd.read_csv('/home/hmid/ssan-data/pykeen_edges.tsv', sep='\t', header=None, names=['head', 'relation', 'tail'])
tf = TriplesFactory.from_labeled_triples(edges_df.values)
train, test = tf.split(ratios=[0.8, 0.2], random_state=42)

result = pipeline(
    model='TransE',
    training=train,
    testing=test,
    model_kwargs=dict(embedding_dim=64),
    training_kwargs=dict(num_epochs=100, batch_size=128),
    random_seed=42,
)

model = result.model
labels = list(result.training.entity_to_id.keys())
with torch.no_grad():
    embeddings = model.entity_representations[0](indices=None).cpu().numpy()

latent_df = pd.DataFrame(embeddings)
latent_df.insert(0, 'h3_index', labels)
latent_df.to_parquet('/home/hmid/ssan-data/latent_vectors.parquet', index=False)
print(f"Trained PyKEEN. Saved {len(latent_df)} latent vectors.")
