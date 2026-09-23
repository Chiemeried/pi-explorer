# pi-explorer

> Ðarlingtøn🦅 Pi Network Tooling

## Description
Flask-based Pi Network blockchain explorer with 6 tabs, private node IP masking, and 410/404 fallback handling.

## Port
`3060`

## Environment Variables
Create a `.env` file in the root of this project:
```
HORIZON_URL=\nPRIVATE_NODE_URL=
```

## Install
```bash
npm install
```

## Run
```bash
# Start with PM2
pm2 start server.py --name pi-explorer --interpreter python3

# Or directly
node server.js
```

## Deploy (from scratch on a new VPS)
```bash
git clone https://github.com/Chiemeried/pi-explorer.git
cd pi-explorer
npm install
cp .env.example .env   # fill in your values
pm2 start server.py --name pi-explorer --interpreter python3
```

---
*Private repo — Ðarlingtøn🦅 Darlington Logs*
