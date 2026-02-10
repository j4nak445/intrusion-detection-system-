import pandas as pd
import matplotlib.pyplot as plt

def show_attack_distribution():
    try:
        df = pd.read_csv("data/full_kdd.csv")
    except Exception as e:
        print("Dataset load error:", e)
        return

    if 'label' not in df.columns:
        print("Label column not found.")
        return

    attack_counts = df['label'].value_counts().sort_values(ascending=False)

    plt.figure(figsize=(12,6))
    attack_counts.plot(kind='bar')
    plt.title("Attack Type Distribution (NSL-KDD)")
    plt.xlabel("Attack Class")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()
