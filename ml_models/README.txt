This directory stores trained ML model files (.pkl, .h5, .pt).
These files are auto-generated when you run the training scripts.
They are NOT committed to Git (see .gitignore).

To generate:
  python -m app.ml.train.train_recommender
  python -m app.ml.train.train_fraud
