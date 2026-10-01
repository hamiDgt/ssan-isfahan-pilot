import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.base import clone

latent = pd.read_parquet('/home/hmid/ssan-data/latent_vectors.parquet')
caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')

df = latent.merge(caps[['final_id', 'gss']], left_on='h3_index', right_on='final_id')

feature_cols = df.select_dtypes(include=[np.number]).columns
feature_cols = [c for c in feature_cols if c != 'gss']

X = df[feature_cols].values
y = df['gss'].values

estimator = Ridge(alpha=1.0)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
scores = []

for train_idx, val_idx in kf.split(X):
    model_cv = clone(estimator).fit(X[train_idx], y[train_idx])
    y_pred_cv = model_cv.predict(X[val_idx])
    scores.append(np.abs(y[val_idx] - y_pred_cv))
scores = np.concatenate(scores)

q = np.quantile(scores, 0.90)
final_model = estimator.fit(X, y)
y_pred = final_model.predict(X)

rel_df = pd.DataFrame({
    'h3_index': df['h3_index'],
    'gss_pred': y_pred,
    'gss_lower': y_pred - q,
    'gss_upper': y_pred + q
})
rel_df.to_parquet('/home/hmid/ssan-data/reliability_cells.parquet', index=False)
print(f"Calculated reliability bounds for {len(rel_df)} capsules. 90% margin: ±{q:.2f}")
