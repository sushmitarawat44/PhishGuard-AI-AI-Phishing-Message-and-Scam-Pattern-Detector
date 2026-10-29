
from pathlib import Path
import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def load_or_train_model(base_dir):
    """Train a local phishing detection model using the sample dataset."""

    dataset = Path(base_dir) / "data" / "messages.csv"

    if not dataset.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset}"
        )

    df = pd.read_csv(dataset)
    df = df.dropna(subset=["text", "label"])

    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    if df.empty:
        raise ValueError("The training dataset is empty.")

    if not {"phishing", "legitimate"}.issubset(set(df["label"])):
        raise ValueError(
            "Dataset labels must include 'phishing' and 'legitimate'."
        )

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
                sublinear_tf=True
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    pipeline.fit(df["text"], df["label"])

    note = (
        f"Local model trained on {len(df)} illustrative messages. "
        "This educational dataset is not a production-grade corpus."
    )

    return pipeline, None, note


def analyze_message(message, model, vectorizer=None):
    """Analyze a message using ML predictions and transparent warning rules."""

    text = str(message).strip()

    if not text:
        return {
            "label": "Uncertain",
            "css": "medium",
            "risk_score": 0,
            "model_score": 0.0,
            "warnings": ["No message provided"],
            "explanation": "Enter a message to analyze.",
            "model_prediction": "uncertain"
        }

    lower = text.lower()

    # Warning patterns are indicators, not proof of fraud.
    patterns = [
        (
            "Urgent or threatening language",
            r"\b(urgent|immediately|within 24 hours|suspended|suspend|"
            r"locked|action required|final warning|disconnect(?:ed|ion)?)\b"
        ),
        (
            "Requests for passwords or one-time codes",
            r"\b(password|passcode|otp|one[- ]time code|"
            r"verification code|pin)\b"
        ),
        (
            "Prize, reward, or unexpected money claim",
            r"\b(prize|winner|won|reward|lottery|claim your|"
            r"cash prize|free gift|you have been selected)\b"
        ),
        (
            "Requests for payment or gift cards",
            r"\b(gift cards?|wire transfer|crypto(?:currency)?|"
            r"pay a fee|processing fee|registration fee|"
            r"payment required|refundable fee)\b"
        ),
        (
            "Link or web address included",
            r"(?:https?://|www\.)[^\s<>]+"
        ),
        (
            "Account or bank impersonation language",
            r"\b(bank account|account security|verify your account|"
            r"unusual activity|billing problem|kyc verification|"
            r"account will be blocked)\b"
        ),
        (
            "Sensitive information requested",
            r"\b(credit card|social security|bank details|"
            r"personal information|identity documents)\b"
        ),
        (
            "Pressure to avoid normal verification",
            r"\b(do not call|don't call|keep this confidential|"
            r"do not tell|secret|share this otp)\b"
        )
    ]

    warnings = []

    for label, pattern in patterns:
        if re.search(pattern, lower, flags=re.IGNORECASE):
            warnings.append(label)

    # Get the model's phishing probability.
    try:
        prediction = str(model.predict([text])[0]).lower()
        probabilities = model.predict_proba([text])[0]
        classes = [str(c).lower() for c in model.classes_]

        if "phishing" in classes:
            phishing_index = classes.index("phishing")
            model_score = float(probabilities[phishing_index])
        else:
            model_score = 0.0
            prediction = "uncertain"

    except (ValueError, AttributeError, IndexError):
        prediction = "uncertain"
        model_score = 0.0

    # Weighted heuristic score. This is not a calibrated probability.
    weights = {
        "Urgent or threatening language": 8,
        "Requests for passwords or one-time codes": 20,
        "Prize, reward, or unexpected money claim": 12,
        "Requests for payment or gift cards": 15,
        "Link or web address included": 8,
        "Account or bank impersonation language": 12,
        "Sensitive information requested": 20,
        "Pressure to avoid normal verification": 12
    }

    rule_points = min(
        sum(weights.get(warning, 0) for warning in warnings),
        65
    )

    # Blend rule-based indicators and the machine-learning result.
    model_points = model_score * 35

    risk_score = int(
        max(0, min(100, round(rule_points + model_points)))
    )

    # Assign a readable risk category.
    if risk_score >= 65:
        label = "High Risk"
        css = "high"
        explanation = (
            "Several significant warning indicators were detected. "
            "Do not click suspicious links or share sensitive details. "
            "Verify through an official channel."
        )

    elif risk_score >= 30:
        label = "Potential Risk"
        css = "medium"
        explanation = (
            "Some suspicious indicators were detected. "
            "Check the sender and verify requests independently."
        )

    else:
        label = "Lower Risk"
        css = "low"
        explanation = (
            "Fewer warning indicators were detected. "
            "This does not guarantee that the message is legitimate."
        )

    if not warnings:
        warnings = ["No listed rule-based warning pattern detected"]

    return {
        "label": label,
        "css": css,
        "risk_score": risk_score,
        "model_score": round(model_score, 3),
        "warnings": warnings,
        "explanation": explanation,
        "model_prediction": prediction
    }

