🛡️ Neural Network Based Intrusion Detection System (IDS) 🛡️

A Machine Learning powered Intrusion Detection System with a retro-style GUI dashboard that simulates real-time network monitoring, attack detection, and SOC-style analytics.

This project integrates:

🔐 Security 
📊 Data Science  
🧠 Neural Network 

Project Features:
1.Neural Network (MLP) attack classifier  
2.Trained on NSL-KDD dataset  
3.Detects major network attacks(trained with NSL KDD dataset):
    - DoS (neptune, smurf, back, etc.)
    - Probe (portsweep, ipsweep)
    - R2L (guess_passwd, warezclient)
    - U2R (rootkit, buffer_overflow)
4.Upload custom traffic CSV  
5.Real-time detection simulation  
6.Flashing alert when attack detected  
7.Live counters (Total / Normal / Attacks)  
8.Attack severity colors  
9.SOC-style dashboard  
10.Logs with attack highlighting  


Screenshots :

Main GUI
[GUI](screenshots/gui.png)

Training Process
[Training](screenshots/train.png)

Attack Detection
[Detection](screenshots/detection.png)

Statistics
[Stats](screenshots/stats.png)

Logs
[Logs](screenshots/logs.png)


⚙️ Installation Guide

Step 1 — Download / Clone Project
git clone 
cd ml-intrusion-detection-system
OR download ZIP and extract.

Step 2 — Create Virtual Environment
python -m venv venv

Step 3 — Activate Environment
Step 4 — Install Required Libraries
pip install -r requirements.txt
Step 5 - Running the Application
python -m src.gui


How to Use the System (Demo)

Step 1 — Train the Model
Click Train Model → Select dataset file.
The neural network learns attack patterns.

🔹 Step 2 — Simulate Detection
Click Detect Attack
The system analyzes sample network traffic.

🔹 Step 3 — Upload Custom CSV
Click Upload Custom CSV to analyze your own dataset.

🔹 Step 4 — View Logs
Click View Logs to see detection history.
Attacks appear in red.

🔹 Step 5 — View Statistics
Click Show Statistics to visualize attack distribution.


System Workflow

Dataset preprocessing (encoding + scaling)
Neural network training
Real-time detection
Logging & alerting
Dashboard visualization