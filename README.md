# AI-Powered Smart Intrusion Detection & Network Traffic Analysis System

Quick start

1. Create and activate virtual environment (PowerShell):

```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```

If activation is blocked: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

2. Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3. Place your dataset CSV(s) into the `data/` folder (e.g. `data/nsl_kdd.csv`).

4. Train the model (example):

```powershell
# from project root
python -m src.model --csv data\nsl_kdd.csv
```

5. Run the GUI:

```powershell
python src\gui.py
```

Project layout

- `data/` - put CSV dataset here
- `models/` - trained model and preprocessor saved here
- `logs/` - detection logs
- `src/` - source modules
- `requirements.txt` - Python dependencies

See `src/` for implementation details and further instructions.