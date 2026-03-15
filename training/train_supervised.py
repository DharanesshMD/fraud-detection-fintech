"""Small training scaffold for a placeholder supervised model.

This script generates synthetic data, trains a simple classifier, and saves the model
with joblib. It optionally logs a minimal run to MLflow if the package is installed.

Usage:
    python training/train_supervised.py --output model.joblib --n-samples 1000

Note: scikit-learn and joblib are optional dev deps and are not installed by default
in requirements.txt to keep runtime images lightweight. Install them with:
    pip install scikit-learn joblib

"""
import argparse
import json
import os
import sys


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--output", "-o", default="models/dummy_model.joblib", help="Path to write the trained model")
    p.add_argument("--n-samples", "-n", type=int, default=1000, help="Number of synthetic samples to generate")
    p.add_argument("--random-state", type=int, default=42)
    return p.parse_args()


def main():
    args = parse_args()

    try:
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        import joblib
    except Exception as e:
        print("Missing training dependencies. Install scikit-learn and joblib to run this script:")
        print("    pip install scikit-learn joblib")
        sys.exit(2)

    # Create synthetic features that mimic velocity features
    X, y = make_classification(n_samples=args.n_samples, n_features=4, n_informative=3, n_redundant=0, random_state=args.random_state)

    # Train a simple classifier
    clf = LogisticRegression(max_iter=200)
    clf.fit(X, y)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    joblib.dump(clf, args.output)
    print(f"Saved model to {args.output}")

    # Try to log to MLflow if available (non-fatal)
    try:
        import mlflow
        with mlflow.start_run():
            mlflow.log_param("n_samples", args.n_samples)
            mlflow.log_param("model", "logistic_regression")
            # mlflow.sklearn.log_model(clf, "model")  # optional
            print("Logged run to MLflow (if a tracking server is configured)")
    except Exception:
        # mlflow not installed or not configured; ignore
        pass


if __name__ == "__main__":
    main()
