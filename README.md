# Blockchain Dynamic Interest Rate System

A proof-of-concept demo that combines a machine learning model with a simulated blockchain ledger to dynamically adjust loan interest rates based on borrower repayment behaviour. Better repayment history → lower interest rate.

---

## How It Works

Traditional lending systems are siloed — a borrower's good repayment record at Bank A is invisible to Bank B. This system proposes a shared, tamper-proof ledger that all approved institutions write to and read from. A Random Forest ML model then reads each borrower's on-chain history and recalculates their interest rate in real time.

```
Borrower makes a repayment
        ↓
Approved institution writes record to blockchain ledger
        ↓
ML model reads updated borrower profile
        ↓
New interest rate predicted and displayed
```

---

## Project Structure

```
├── index.html          # Frontend dashboard (no build step required)
├── app.py              # Flask API wrapping the trained ML model
├── ml_model.py         # Standalone ML prototype and scenario simulator
├── LoanRepayment.sol   # Solidity smart contract (data layer concept)
└── loan_data.csv       # Lending Club dataset used for training
```

### File Roles

**`index.html`** is the main interface. It connects to the Flask API to get interest rate predictions, simulates blockchain transactions with realistic tx hashes, block numbers, and gas fees, and persists all records via localStorage so data survives page refreshes.

**`app.py`** is the live backend. It trains a Random Forest Regressor on startup using `loan_data.csv` and exposes three endpoints: `POST /predict` for single predictions, `GET /scenario` for a 12-month simulation, and `GET /health` for model diagnostics. Run this first before opening the frontend.

**`ml_model.py`** is a standalone prototype used during development. It trains a simpler version of the model with fewer features and includes a `BlockchainBridge` class simulating on-chain data reads. It is not called by `app.py` or the frontend — it can be run independently with `python ml_model.py` to see a scenario simulation printed to the terminal.

**`LoanRepayment.sol`** defines the smart contract that would handle data storage in a production deployment. It manages approved institutions, immutable repayment records, borrower profiles, and on-time rate calculations. In this demo it is not deployed — the frontend simulates its behaviour locally.

**`loan_data.csv`** is the Lending Club dataset (9,578 records, 14 columns). It is used by `app.py` to train the model on startup.

---

## Quickstart

**1. Install dependencies**
```bash
pip install flask flask-cors pandas scikit-learn
```

**2. Start the Flask API**
```bash
python app.py
```
The server starts at `http://localhost:5000`. The model trains automatically on startup — expect a few seconds on first run.

**3. Open the frontend**

Open `index.html` directly in a browser. No build step or server required.

---

## Features

**Institution login** — Select which bank you are logging in as (HSBC, Hang Seng, Bank of China). Each institution has a unique wallet address. Only approved institutions may write records to the ledger.

**Borrower system** — Three pre-loaded borrowers with different credit profiles. Switch between borrowers to see their independent rate histories. New borrowers can be registered via a form; the ML model calculates their initial rate immediately.

**Shared ledger** — All repayment records are stored in a single ledger regardless of which institution submitted them. The ledger can be filtered by borrower or viewed in full. Records persist across page refreshes via localStorage.

**Realistic blockchain simulation** — Each submission generates a 64-character transaction hash (matching real Ethereum format), a block number, simulated gas usage, and a gas fee in ETH. Clicking any tx hash opens a full transaction receipt modal. The network status bar shows live-updating block number and gas price.

**ML rate prediction** — Every form submission sends the borrower's current financial profile to the Python model and returns an updated interest rate. The rate history chart updates in real time.

---

## ML Model Details

The model is a `RandomForestRegressor` trained on the Lending Club dataset. It uses 17 features including FICO score, debt-to-income ratio, annual income (log-transformed), revolving credit utilisation, recent credit enquiries, delinquency history, and loan purpose (one-hot encoded).

| Metric | Value |
|--------|-------|
| Algorithm | Random Forest Regressor |
| Trees | 100 |
| Max depth | 10 |
| Training set | 80% of 9,578 records |
| Target | Interest rate (%) |

Model performance can be checked via `GET http://localhost:5000/health`.

---

## Smart Contract Overview (`LoanRepayment.sol`)

The Solidity contract defines the data layer that would replace the localStorage simulation in a production system. Key design decisions:

- `msg.sender` is recorded automatically as the submitting institution — it cannot be forged
- `block.timestamp` is set by the blockchain, not the caller — repayment times cannot be backdated
- Records are append-only; no delete or update functions exist
- `onlyApprovedInstitution` modifier prevents unauthorised writes
- `getOnTimeRate()` is a `view` function (free to call) that returns a borrower's on-time percentage for use as an ML feature

To deploy the contract, use [Hardhat](https://hardhat.org/) or [Remix IDE](https://remix.ethereum.org/) and target a local or test network.

---

## Known Limitations

- `ml_model.py` and `app.py` use different feature sets and train separate models independently. The frontend uses `app.py` exclusively.
- The smart contract is not deployed. The frontend simulates blockchain behaviour in-memory with localStorage persistence.
- localStorage is browser-specific — data does not sync across devices or users.
- The "institution login" is UI-only. There is no authentication; any user can select any institution.
