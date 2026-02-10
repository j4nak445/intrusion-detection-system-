import os
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

ROOT = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

def load_csv(path):
    return pd.read_csv(path)

def preprocess(df, label_col='label', save_objects=True):
    df = df.copy()
    df.dropna(inplace=True)

    # identify categorical columns (exclude label)
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if label_col in cat_cols:
        cat_cols.remove(label_col)

    encoders = {}
    for c in cat_cols:
        le = LabelEncoder()
        df[c] = le.fit_transform(df[c].astype(str))
        encoders[c] = le

    # label encoder (store under key 'label')
    le_label = LabelEncoder()
    df[label_col] = le_label.fit_transform(df[label_col].astype(str))
    encoders['label'] = le_label

    X = df.drop(columns=[label_col])
    y = df[label_col]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if save_objects:
        joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
        joblib.dump(encoders, os.path.join(MODELS_DIR, 'encoders.pkl'))
        # save feature order so future samples can be aligned before scaling
        feature_names = X.columns.tolist()
        joblib.dump(feature_names, os.path.join(MODELS_DIR, 'feature_names.pkl'))

    return X_scaled, y.values, scaler, encoders


def get_train_test(csv_path, label_col='label', test_size=0.3, random_state=42):
    df = load_csv(csv_path)
    X, y, scaler, encoders = preprocess(df, label_col=label_col, save_objects=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state
    )

    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True)
    args = parser.parse_args()

    X_train, X_test, y_train, y_test = get_train_test(args.csv)
    print('Train shapes:', X_train.shape, y_train.shape)
    print('Test shapes:', X_test.shape, y_test.shape)
