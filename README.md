# SegmentIQ — Customer Segmentation using Clustering

A multi-page Big Data Analytics mini-project built with Streamlit, Pandas, scikit-learn and Plotly.

## Features
- Upload CSV/Excel transaction data or load `data/Online Retail.xlsx`
- Transaction cleaning with a data quality audit
- RFM (Recency, Frequency, Monetary) customer features
- K-Means clustering with log transform and feature scaling
- Cluster profile, revenue/customer mix, interactive customer scatter plot
- Model evaluation using inertia/Elbow and silhouette score
- Customer search/filter and CSV/JSON exports
- Dark navy responsive dashboard

## Dataset
Use the official UCI Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

The original dataset has 541,909 transaction records. It includes cancellations and missing customer IDs. This project excludes cancellation invoice rows, rows without customer/date, and non-positive quantities/prices from purchase-based RFM metrics.

## Run locally (Windows)
1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/ (enable **Add Python to PATH**).
2. Extract this ZIP.
3. Open Command Prompt in the extracted `customer_segmentation_bda` folder.
4. Create an environment:
   ```bat
   py -3.12 -m venv .venv
   .venv\\Scripts\\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Download `Online Retail.xlsx` from UCI and place it in `data` OR upload it from the app sidebar.
6. Run:
   ```bat
   streamlit run app.py
   ```
7. Open the local URL shown in Command Prompt, usually http://localhost:8501.

## Pages
- Overview
- Customer Segments
- Data Explorer
- Model Evaluation
- Export Results

## Notes / methodology
- Recency reference date is one day after the latest valid purchase date in the dataset.
- Frequency is the count of distinct purchase invoices per customer.
- Monetary is quantity × unit price, summed per customer, in the dataset's source currency (GBP).
- Clustering features are log1p-transformed and standardized.
- Cluster names are heuristic descriptions based on relative median monetary/frequency values; they are not ground-truth labels.
- Silhouette scores are approximate when computed on a sample of customers.
- For a formal submission, document data-cleaning choices and validate segment interpretations.

## Deploy online
1. Push the project folder to a GitHub repository. Do not commit the raw dataset if you do not want to distribute it.
2. Visit https://share.streamlit.io/ and connect GitHub.
3. Create app → choose repository, branch `main`, and `app.py`.
4. Deploy. Streamlit Community Cloud installs packages from `requirements.txt`.
5. Test the deployed app with the dataset upload control.

## Current scope
This starter is a working analytics app foundation, not a claim of completed deployment. Test with the real dataset before final submission.
