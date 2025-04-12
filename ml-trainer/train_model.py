import pandas as pd     # type: ignore
import joblib   # type: ignore
from sklearn.model_selection import train_test_split    # type: ignore
from sklearn.ensemble import RandomForestClassifier   # type: ignore

# === CONFIG ===
CSV_PATH = "./data/bybit_dataset_custom.csv"
MODEL_PATH = "./model/crypto_direction_model.pkl"

# === LOAD DATA ===
df = pd.read_csv(CSV_PATH)

# === FEATURES e TARGET ===
features = ["price", "quantity", "is_buy"]
X = df[features]
y = df["target"]

# === SPLIT ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# === TRAIN MODEL ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === SAVE MODEL ===
joblib.dump(model, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")
