# Blockchain Dynamic Interest Rate System

A proof-of-concept lending demo that combines:

- a shared blockchain-style repayment ledger
- a Python Random Forest model for interest rate prediction
- a browser dashboard for institution login, borrower management, and repayment submission

The idea is simple: better repayment behaviour should lead to a better predicted interest rate, and repayment records should be visible across approved institutions instead of being trapped inside one bank's silo.

## Overview

Traditional lending systems often keep borrower repayment history inside individual institutions. This project demonstrates a different model:

- approved institutions submit repayment records to a shared ledger
- the borrower profile updates over time
- the ML model reads the latest borrower features
- the dashboard shows a newly predicted interest rate

In the current implementation, the blockchain is simulated in the frontend using `localStorage`, while the ML model runs live through a Flask API.

## Current System Features

### 1. Institution login flow

The dashboard is hidden until an institution logs in.

- users first select an institution
- users then enter institution credentials
- after login, the main dashboard becomes visible
- a `Sign out` button returns the user to the institution selection flow

Current demo institutions:

- HSBC Hong Kong
- Hang Seng Bank
- Bank of China (HK)

### 2. Borrower management

The system includes:

- preloaded default borrowers
- support for registering new borrowers
- support for switching between borrowers
- support for storing a borrower `ID Number` in the borrower profile

When registering a new borrower, the form now captures:

- full name
- ID number
- FICO score
- income and debt metrics
- repayment-related credit features used by the ML model

### 3. Existing borrower ID completion flow

Some older borrowers in `localStorage` may not have an ID number yet.

To handle that without deleting existing data:

- borrowers without an ID show `Missing ID`
- selecting such a borrower reveals an inline `Save ID Number` form
- once saved, the ID number is written back to `localStorage`

### 4. Privacy-conscious ID display

Borrower ID numbers are stored in the borrower profile, but the UI does not expose them everywhere.

Current behaviour:

- the top-right borrower pill does not show the ID number
- borrower lists show only a masked version
- transaction receipts show only a masked version

### 5. Shared ledger simulation

All repayment submissions are appended to a shared ledger regardless of which institution submits them.

The ledger supports:

- viewing all records
- filtering by borrower
- opening a transaction receipt modal for each record

Each simulated transaction includes:

- transaction hash
- block number
- timestamp
- due date
- institution
- borrower
- borrower ID (masked)
- repayment amount
- payment status
- gas used
- gas fee
- network

### 6. ML-powered interest rate prediction

Each repayment submission sends the borrower's latest financial profile to the Flask backend, which returns a predicted interest rate.

The frontend updates:

- current interest rate
- repayment stats
- borrower chart history
- latest submission result

## Tech Stack

### Frontend

- HTML
- CSS
- Vanilla JavaScript
- Chart.js
- `localStorage` for persistence

### Backend

- Python
- Flask
- Flask-CORS
- pandas
- scikit-learn

### Smart contract

- Solidity

## Project Structure

```text
index.html          Frontend dashboard and blockchain simulation
app.py              Flask API wrapping the trained ML model
LoanRepayment.sol   Smart contract design for production-style storage
loan_data.csv       Lending Club dataset used for training
README.md           Project documentation
```

## How the Prediction Model Works

`app.py` trains a `RandomForestRegressor` on startup using `loan_data.csv`.

The backend uses:

- 10 numeric features
- 7 one-hot encoded loan purpose features
- 17 total model input features

Key borrower inputs include:

- `credit.policy`
- `fico`
- `dti`
- `log.annual.inc`
- `days.with.cr.line`
- `revol.bal`
- `revol.util`
- `inq.last.6mths`
- `delinq.2yrs`
- `pub.rec`
- `purpose`

Model settings in the current backend:

- algorithm: `RandomForestRegressor`
- `n_estimators=100`
- `max_depth=10`
- `min_samples_leaf=5`
- `random_state=42`

## API Endpoints

The Flask server runs at `http://localhost:5000`.

### `GET /health`

Returns backend health and model metadata, including:

- status
- model type
- dataset name
- record count
- feature count
- MAE
- R2
- feature importance

### `POST /predict`

Accepts a borrower feature payload and returns:

```json
{
  "predicted_rate": 12.34,
  "unit": "%"
}
```

### `GET /scenario`

Returns a sample multi-period scenario simulation from the backend.

## Quick Start

### 1. Install dependencies

```bash
pip install flask flask-cors pandas scikit-learn
```

### 2. Start the backend

```bash
python app.py
```

### 3. Open the frontend

Open `index.html` directly in a browser.

No separate frontend build step is required.

## Demo Institution Credentials

Current demo credentials in `index.html`:

- HSBC Hong Kong: `hsbc_admin / hsbc1234`
- Hang Seng Bank: `hangseng_admin / hangseng1234`
- Bank of China (HK): `boc_admin / boc1234`

## Smart Contract Role

`LoanRepayment.sol` represents the on-chain data layer for a fuller production version of the system.

It defines:

- approved institution access control
- immutable repayment records
- borrower repayment history
- borrower aggregate repayment statistics
- derived on-time repayment rate

Important note:

- the smart contract is not currently deployed
- the live demo uses frontend simulation instead

## Current Limitations

- Institution login is frontend-only demo logic and not real secure authentication.
- Ledger persistence relies on browser `localStorage`, so data is browser-specific.
- Existing local borrowers may still need manual ID completion.
- The smart contract is included as a design artifact and is not connected to the live frontend.
- The dashboard simulates blockchain properties; it is not writing to a real chain.

## Suggested Demo Flow

For presentation use, a smooth flow is:

1. Start `app.py`
2. Open `index.html`
3. Log in as one institution
4. Select an existing borrower
5. If needed, fill in missing borrower ID once
6. Submit a repayment
7. Show the updated rate, ledger row, and transaction receipt
8. Sign out and log in as another institution to show the shared-ledger idea
