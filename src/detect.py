import os
import joblib
import numpy as np
import tensorflow as tf
from datetime import datetime
import uuid
import csv

ROOT = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, 'models')
LOGS_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

def load_artifacts():
    scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
    encoders = joblib.load(os.path.join(MODELS_DIR, 'encoders.pkl'))
    # feature names saved during preprocessing
    feature_path = os.path.join(MODELS_DIR, 'feature_names.pkl')
    feature_names = None
    if os.path.exists(feature_path):
        feature_names = joblib.load(feature_path)
    model = tf.keras.models.load_model(os.path.join(MODELS_DIR, 'best_ids_model.h5'))
    return scaler, encoders, model, feature_names


def predict_sample(sample_df):
    scaler, encoders, model, feature_names = load_artifacts()

    df = sample_df.copy()

    # Drop label column if present
    if 'label' in df.columns:
        df = df.drop(columns=['label'])

    # Apply saved encoders for categorical columns (encoders contains 'label' + other encoders)
    for col, le in encoders.items():
        if col == 'label':
            continue
        if col in df.columns:
            # safe transform: map unseen values to index 0
            mapping = {str(v): i for i, v in enumerate(le.classes_)}
            df[col] = df[col].astype(str).apply(lambda v: mapping.get(v, 0))

    # Reindex columns to match training feature order. Fill missing with 0, drop extras.
    if feature_names is not None:
        df = df.reindex(columns=feature_names, fill_value=0)

    # Convert to numeric and scale
    X = df.values.astype(float)
    try:
        Xs = scaler.transform(X)
    except Exception as e:
        raise ValueError(f"Feature mismatch when transforming sample: {e}\nEnsure the sample has the same feature columns produced during training.")

    # Predict
    probs = model.predict(Xs)
    pred = int(np.argmax(probs, axis=1)[0])

    # Decode label
    label_encoder = encoders.get('label')
    if label_encoder:
        human_label = label_encoder.inverse_transform([pred])[0]
    else:
        human_label = str(pred)

    is_attack = str(human_label).lower() != 'normal'

    return {
        'pred': pred,
        'label': human_label,
        'is_attack': is_attack,
        'probs': probs[0].tolist()
    }


def append_log(connection_id, label, result):
    log_path = os.path.join(LOGS_DIR, 'ids_logs.csv')
    header = ['timestamp', 'connection_id', 'label', 'result']
    exists = os.path.exists(log_path)

    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(header)
        writer.writerow([datetime.utcnow().isoformat(), connection_id, label, result])


if __name__ == '__main__':
    import pandas as pd
    df = pd.read_csv('data/sample_connection.csv')
    r = predict_sample(df.iloc[[0]])
    append_log(str(uuid.uuid4()), r['label'], 'attack' if r['is_attack'] else 'normal')
    print(r)
