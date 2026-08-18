# Ðarlingtøn🦅

Pi Network block explorer. Flask backend, queries a private Horizon node.

## Run locally
```
pip install -r requirements.txt --break-system-packages
python3 app.py
```
Serves on port 3060.

## Deploy (VPS, PM2)
```
git clone <repo> pi-explorer
cd pi-explorer
pip install -r requirements.txt --break-system-packages
pm2 start app.py --name pi-explorer --interpreter python3
pm2 save
```

Node endpoint is set in `horizon.py` (`HORIZON_BASE`).
