"""
app.py — Blockchain Dynamic Interest Rate System
Flask API wrapping the trained Random Forest model.

Usage:
    python app.py

Endpoints:
    POST /predict   — predict interest rate from borrower features
    GET  /scenario  — return full 12-month scenario simulation
    GET  /health    — model stats (for backend checking only)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import os

app = Flask(__name__)
CORS(app)

# ── Purpose categories (must match training data) ─────────────────────────────
PURPOSE_CATEGORIES = [
    'all_other', 'credit_card', 'debt_consolidation',
    'educational', 'home_improvement', 'major_purchase', 'small_business'
]

NUMERIC_FEATURES = [
    'credit.policy',
    'fico',
    'dti',
    'log.annual.inc',
    'days.with.cr.line',
    'revol.bal',
    'revol.util',
    'inq.last.6mths',
    'delinq.2yrs',
    'pub.rec',
]
PURPOSE_FEATURES = [f'purpose_{c}' for c in PURPOSE_CATEGORIES]
ALL_FEATURES = NUMERIC_FEATURES + PURPOSE_FEATURES
TARGET = 'int.rate'

# ── Train on startup ──────────────────────────────────────────────────────────
print("[startup] Loading dataset and training model...")

CSV_PATH = os.path.join(os.path.dirname(__file__), "loan_data.csv")
df = pd.read_csv(CSV_PATH)

if df[TARGET].max() < 1.0:
    df[TARGET] = df[TARGET] * 100

purpose_dummies = pd.get_dummies(df['purpose'], prefix='purpose')
df = pd.concat([df, purpose_dummies], axis=1)
for col in PURPOSE_FEATURES:
    if col not in df.columns:
        df[col] = 0

X = df[ALL_FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=5, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred  = model.predict(X_test)
mae     = round(mean_absolute_error(y_test, y_pred), 4)
r2      = round(r2_score(y_test, y_pred), 4)
importances = {f: round(float(v), 4) for f, v in zip(ALL_FEATURES, model.feature_importances_)}

print(f"[startup] Model ready — {len(ALL_FEATURES)} features  |  MAE: {mae}%  |  R2: {r2}")


def build_feature_vector(data: dict) -> pd.DataFrame:
    row = {f: data.get(f, 0) for f in NUMERIC_FEATURES}
    purpose = data.get('purpose', 'all_other')
    for cat in PURPOSE_CATEGORIES:
        row[f'purpose_{cat}'] = 1 if purpose == cat else 0
    return pd.DataFrame([row])[ALL_FEATURES]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok", "model": "RandomForestRegressor",
        "dataset": "Lending Club", "records": len(df),
        "features": len(ALL_FEATURES), "mae": mae, "r2": r2,
        "feature_importance": importances,
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    rate = round(float(model.predict(build_feature_vector(data))[0]), 2)
    return jsonify({"predicted_rate": rate, "unit": "%"})


@app.route("/scenario", methods=["GET"])
def scenario():
    scenarios = [
        ("Month 0",   0,  {"credit.policy":1,"fico":620,"dti":18,"log.annual.inc":10.5,"days.with.cr.line":1200,"revol.bal":8000,"revol.util":72,"inq.last.6mths":3,"delinq.2yrs":5,"pub.rec":0,"purpose":"debt_consolidation"}),
        ("Month 3",   3,  {"credit.policy":1,"fico":630,"dti":17,"log.annual.inc":10.5,"days.with.cr.line":1290,"revol.bal":7500,"revol.util":68,"inq.last.6mths":2,"delinq.2yrs":4,"pub.rec":0,"purpose":"debt_consolidation"}),
        ("Month 6",   6,  {"credit.policy":1,"fico":650,"dti":16,"log.annual.inc":10.6,"days.with.cr.line":1380,"revol.bal":6500,"revol.util":60,"inq.last.6mths":2,"delinq.2yrs":3,"pub.rec":0,"purpose":"debt_consolidation"}),
        ("Month 9",   9,  {"credit.policy":1,"fico":675,"dti":14,"log.annual.inc":10.7,"days.with.cr.line":1470,"revol.bal":5500,"revol.util":52,"inq.last.6mths":1,"delinq.2yrs":1,"pub.rec":0,"purpose":"debt_consolidation"}),
        ("Month 12", 12,  {"credit.policy":1,"fico":700,"dti":13,"log.annual.inc":10.8,"days.with.cr.line":1560,"revol.bal":4500,"revol.util":42,"inq.last.6mths":1,"delinq.2yrs":0,"pub.rec":0,"purpose":"debt_consolidation"}),
    ]
    result = []
    for label, payments, feat in scenarios:
        rate = round(float(model.predict(build_feature_vector(feat))[0]), 2)
        result.append({"label":label,"fico":feat["fico"],"dti":feat["dti"],
                        "purpose":feat["purpose"],
                        "on_time_pct": round(payments/12*100,1) if payments>0 else 0,
                        "predicted_rate":rate})
    return jsonify(result)


if __name__ == "__main__":
    print("[server] Starting on http://localhost:5000")
    app.run(debug=True, port=5000) 