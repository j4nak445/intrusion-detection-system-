import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from sklearn.metrics import classification_report, accuracy_score

ROOT = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

def build_model(input_dim, num_classes):
    model = models.Sequential()
    model.add(layers.Input(shape=(input_dim,)))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.3))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(num_classes, activation='softmax'))
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def train(X_train, y_train, X_val, y_val, epochs=50, batch_size=128):
    num_classes = int(max(y_train.max(), y_val.max()) + 1)

    model = build_model(X_train.shape[1], num_classes)

    ckpt_path = os.path.join(MODELS_DIR, 'best_ids_model.h5')
    cb = [
        callbacks.EarlyStopping(patience=6, restore_best_weights=True),
        callbacks.ModelCheckpoint(ckpt_path, save_best_only=True)
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=cb
    )

    model.save(os.path.join(MODELS_DIR, 'final_ids_model.h5'))
    return model, history


def evaluate(model, X_test, y_test):
    preds = np.argmax(model.predict(X_test), axis=1)
    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds)
    return acc, report

if __name__ == '__main__':
    import argparse
    from src.data_loader import get_train_test
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True)
    parser.add_argument('--epochs', type=int, default=30)
    args = parser.parse_args()
    X_train, X_test, y_train, y_test = get_train_test(args.csv)
    model, history = train(X_train, y_train, X_test, y_test, epochs=args.epochs)
    acc, report = evaluate(model, X_test, y_test)
    print('Test accuracy:', acc)
    print(report)
