import os
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))
LOGS_DIR = os.path.join(ROOT, 'logs')

def plot_attack_pie(log_csv=None, save_path=None):
    if log_csv is None:
        log_csv = os.path.join(LOGS_DIR, 'ids_logs.csv')
    if not os.path.exists(log_csv):
        return None
    df = pd.read_csv(log_csv)
    counts = df['result'].value_counts()
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['#00FF00','#FF4444'])
    ax.set_title('Normal vs Attack')
    if save_path:
        fig.savefig(save_path)
    return fig

def plot_attack_bar(log_csv=None):
    if log_csv is None:
        log_csv = os.path.join(LOGS_DIR, 'ids_logs.csv')
    if not os.path.exists(log_csv):
        return None
    df = pd.read_csv(log_csv)
    counts = df['label'].value_counts()
    fig, ax = plt.subplots(figsize=(6,4))
    counts.plot.bar(ax=ax, color='gray')
    ax.set_title('Attack types')
    ax.set_ylabel('Count')
    return fig
