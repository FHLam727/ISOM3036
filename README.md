# Blockchain Dynamic Interest Rate System
# 區塊鏈動態利率系統

A proof-of-concept demo combining machine learning with a simulated blockchain ledger to dynamically adjust loan interest rates based on borrower repayment behaviour. Better repayment history → lower interest rate.

本專案為概念驗證示範，結合機器學習模型與模擬區塊鏈帳本，根據借款人的還款行為動態調整貸款利率。還款記錄越佳，利率越低。

---

## How It Works / 系統運作原理

Traditional lending systems are siloed — a borrower's good repayment record at Bank A is invisible to Bank B. This system proposes a shared, tamper-proof ledger that all approved institutions write to and read from. A Random Forest ML model then reads each borrower's on-chain history and recalculates their interest rate in real time.

傳統借貸系統各自獨立，借款人在甲銀行的良好還款記錄，乙銀行無從得知。本系統提出一個共用的、不可篡改的帳本，讓所有認可機構共同寫入及讀取。機器學習模型隨後讀取每位借款人的鏈上歷史，實時重新計算其利率。

```
Borrower makes a repayment / 借款人完成還款
              ↓
Approved institution writes record to ledger / 認可機構將記錄寫入帳本
              ↓
ML model reads updated borrower profile / 機器學習模型讀取最新借款人資料
              ↓
New interest rate predicted and displayed / 預測新利率並顯示
```

---

## Project Structure / 專案結構

```
├── index.html          # Frontend dashboard / 前端儀表板（無需建置步驟）
├── app.py              # Flask API wrapping the trained ML model / 封裝已訓練模型的 Flask API
├── LoanRepayment.sol   # Solidity smart contract / Solidity 智能合約（數據層概念）
└── loan_data.csv       # Lending Club dataset / Lending Club 訓練數據集
```

### File Roles / 各文件說明

**`index.html`** is the main interface. It connects to the Flask API for interest rate predictions, simulates blockchain transactions with realistic tx hashes, block numbers, and gas fees, and persists all records via localStorage.

**`index.html`** 為主要介面，連接 Flask API 取得利率預測，以真實格式模擬區塊鏈交易（包括交易雜湊值、區塊號及燃料費），並透過 localStorage 持久化儲存所有記錄。

**`app.py`** is the live backend. It trains a Random Forest Regressor on startup using `loan_data.csv` and exposes three endpoints: `POST /predict` for single predictions, `GET /scenario` for a 12-month simulation, and `GET /health` for model diagnostics.

**`app.py`** 為即時後端，啟動時自動以 `loan_data.csv` 訓練隨機森林回歸模型，並提供三個端點：`POST /predict` 用於單次預測、`GET /scenario` 用於12個月模擬、`GET /health` 用於模型診斷。

**`LoanRepayment.sol`** defines the smart contract that would handle data storage in a production deployment. In this demo it is not deployed — the frontend simulates its behaviour locally.

**`LoanRepayment.sol`** 定義正式部署時負責數據儲存的智能合約。本示範中合約未經部署，前端以本地方式模擬其行為。

**`loan_data.csv`** is the Lending Club dataset (9,578 records, 14 columns) used by `app.py` to train the model on startup.

**`loan_data.csv`** 為 Lending Club 數據集（9,578 筆記錄，14 個欄位），供 `app.py` 在啟動時訓練模型。

---

## Quickstart / 快速開始

**1. Install dependencies / 安裝依賴套件**
```bash
pip install flask flask-cors pandas scikit-learn
```

**2. Start the Flask API / 啟動 Flask API**
```bash
python app.py
```
The server starts at `http://localhost:5000`. The model trains automatically on startup.

伺服器將於 `http://localhost:5000` 啟動，模型於啟動時自動訓練，首次執行需等待數秒。

**3. Open the frontend / 開啟前端**

Open `index.html` directly in a browser. No build step or server required.

直接以瀏覽器開啟 `index.html`，無需建置步驟或額外伺服器。

---

## Features / 功能說明

**Institution Login / 機構登入**
Select which bank you are logging in as (HSBC, Hang Seng, Bank of China). Each institution has a unique wallet address. Only approved institutions may write records to the ledger.

選擇以哪間銀行身份登入（滙豐、恒生、中銀），每間機構擁有唯一的錢包地址，僅認可機構方可向帳本寫入記錄。

**Borrower System / 借款人系統**
Three pre-loaded borrowers with different credit profiles. Switch between borrowers to view their independent rate histories. New borrowers can be registered via a form; the ML model calculates their initial rate immediately.

系統預載三位信用狀況各異的借款人，可切換借款人以查看各自獨立的利率歷史。亦可透過表單登記新借款人，機器學習模型將即時計算其初始利率。

**Shared Ledger / 共用帳本**
All repayment records are stored in a single ledger regardless of which institution submitted them. The ledger can be filtered by borrower or viewed in full. Records persist across page refreshes via localStorage.

所有還款記錄無論由哪間機構提交，均儲存於同一帳本。帳本可按借款人篩選或全覽。記錄透過 localStorage 持久化，重新整理頁面後不會消失。

**Blockchain Simulation / 區塊鏈模擬**
Each submission generates a 64-character transaction hash (matching real Ethereum format), a block number, simulated gas usage, and a gas fee in ETH. Clicking any tx hash opens a full transaction receipt modal. The network status bar shows a live-updating block number and gas price.

每次提交均生成64位元交易雜湊值（格式與真實以太坊一致）、區塊號、模擬燃料用量及以 ETH 計算的燃料費。點擊任何交易雜湊值可查看完整交易收據。網絡狀態欄顯示實時更新的區塊號及燃料價格。

**ML Rate Prediction / 機器學習利率預測**
Every form submission sends the borrower's current financial profile to the Python model and returns an updated interest rate. The rate history chart updates in real time.

每次提交表單均將借款人的最新財務資料傳送至 Python 模型，並返回更新後的利率，利率歷史圖表即時更新。

---

## ML Model Details / 機器學習模型詳情

The model is a `RandomForestRegressor` trained on the Lending Club dataset using 17 features including FICO score, debt-to-income ratio, annual income (log-transformed), revolving credit utilisation, recent credit enquiries, delinquency history, and loan purpose (one-hot encoded).

模型為 `RandomForestRegressor`，以 Lending Club 數據集訓練，使用17個特徵，包括 FICO 信用評分、負債收入比、年收入（對數轉換）、循環信貸使用率、近期信用查詢次數、逾期記錄及貸款用途（獨熱編碼）。

| Metric / 指標 | Value / 數值 |
|---|---|
| Algorithm / 演算法 | Random Forest Regressor |
| Trees / 決策樹數量 | 100 |
| Max depth / 最大深度 | 10 |
| Training set / 訓練集 | 80% of 9,578 records |
| Target / 預測目標 | Interest rate (%) / 利率（%） |

Model performance can be checked via `GET http://localhost:5000/health`.

模型效能可透過 `GET http://localhost:5000/health` 查閱。

---

## Smart Contract Overview / 智能合約概覽

The Solidity contract defines the data layer that would replace the localStorage simulation in a production system. Key design decisions:

Solidity 合約定義正式系統中取代 localStorage 模擬的數據層，主要設計考量如下：

- `msg.sender` is recorded automatically as the submitting institution — it cannot be forged. / `msg.sender` 自動記錄為提交機構，無法偽造。
- `block.timestamp` is set by the blockchain, not the caller — repayment times cannot be backdated. / `block.timestamp` 由區塊鏈設定，而非調用方，還款時間無法回溯竄改。
- Records are append-only; no delete or update functions exist. / 記錄僅可新增，不存在刪除或更新函數。
- `onlyApprovedInstitution` modifier prevents unauthorised writes. / `onlyApprovedInstitution` 修飾符阻止未授權寫入。
- `getOnTimeRate()` is a `view` function (free to call) returning a borrower's on-time percentage for use as an ML feature. / `getOnTimeRate()` 為 `view` 函數（免費調用），返回借款人準時還款百分比，供機器學習模型使用。

To deploy the contract, use [Hardhat](https://hardhat.org/) or [Remix IDE](https://remix.ethereum.org/) targeting a local or test network.

如需部署合約，可使用 [Hardhat](https://hardhat.org/) 或 [Remix IDE](https://remix.ethereum.org/)，目標設為本地或測試網絡。

---

## Known Limitations / 已知限制

- The smart contract is not deployed. The frontend simulates blockchain behaviour in-memory with localStorage persistence. / 智能合約未經部署，前端以記憶體模擬區塊鏈行為，並透過 localStorage 持久化。
- localStorage is browser-specific — data does not sync across devices or users. / localStorage 為瀏覽器本地儲存，數據不會跨裝置或跨用戶同步。
- The institution login is UI-only with no authentication — any user can select any institution. / 機構登入僅為介面功能，不含身份驗證，任何用戶均可選擇任意機構。