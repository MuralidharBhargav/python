import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from sklearn.ensemble import IsolationForest, RandomForestClassifier
import numpy as np

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'training_data' not in st.session_state:
    st.session_state.training_data = []

st.title("🔍 Auto Data Profiler & DQ Rule Recommender")

# Step 1️⃣ Upload dataset
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📊 **Dataset Preview:**")
    st.dataframe(df.head())

    # Step 1️⃣: Auto-profiling
    st.subheader("🔬 Auto Profiling")
    profile = ProfileReport(df, minimal=True)
    st_profile_report = profile.to_notebook_iframe()

    # Anomaly detection (Isolation Forest)
    st.subheader("🚨 Anomaly Detection")
    numeric_df = df.select_dtypes(include=np.number).fillna(0)
    if not numeric_df.empty:
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomalies = iso_forest.fit_predict(numeric_df)
        df['anomaly'] = anomalies
        st.write(f"Detected {sum(anomalies == -1)} anomalies.")
        st.dataframe(df[df['anomaly'] == -1])
    else:
        st.warning("No numeric columns found for anomaly detection.")

    # Feature correlation
    st.subheader("📈 Feature Correlation")
    corr = df.corr()
    st.dataframe(corr)

    # Step 2️⃣: Prepare profiling features
    features = []
    for col in df.columns:
        col_data = df[col]
        stats = {
            'column': col,
            'missing_ratio': col_data.isnull().mean(),
            'unique_ratio': df[col].nunique() / len(df)
        }
        if pd.api.types.is_numeric_dtype(col_data):
            stats.update({
                'mean': col_data.mean(),
                'std': col_data.std()
            })
        features.append(stats)

    features_df = pd.DataFrame(features)
    st.subheader("🔍 Profiling Features")
    st.dataframe(features_df)

    # Train or use the existing model
    feature_cols = ['missing_ratio', 'unique_ratio', 'mean', 'std']
    feature_df = features_df[feature_cols].fillna(0)

    if st.session_state.model is None:
        # Mock model (for demo): Randomly suggest rules
        st.session_state.model = RandomForestClassifier()
        y_mock = np.random.choice([0, 1], size=len(feature_df))
        st.session_state.model.fit(feature_df, y_mock)

    predictions = st.session_state.model.predict(feature_df)
    features_df['suggested_rule'] = ['Check Completeness' if p == 1 else 'No Action' for p in predictions]

    # Step 3️⃣: Let user select which rules to apply
    st.subheader("✅ Select Rules to Apply")
    rule_options = features_df['suggested_rule'].unique().tolist()
    selected_rules = st.multiselect("Select rules to apply:", rule_options)

    # Apply rules to flag bad records
    if selected_rules:
        st.subheader("🚩 Flagged Bad Records")
        flagged_rows = pd.DataFrame()
        if 'Check Completeness' in selected_rules:
            bad_rows = df[df.isnull().any(axis=1)]
            flagged_rows = pd.concat([flagged_rows, bad_rows])

        if not flagged_rows.empty:
            st.dataframe(flagged_rows)
        else:
            st.success("✅ No bad records found based on selected rules.")

        # Step 4️⃣: Feed back into model
        st.session_state.training_data.append({
            'X': feature_df.values,
            'y': (features_df['suggested_rule'].isin(selected_rules)).astype(int)
        })

        if st.button("🔄 Retrain Model with Feedback"):
            # Aggregate training data
            X_train = np.vstack([d['X'] for d in st.session_state.training_data])
            y_train = np.hstack([d['y'] for d in st.session_state.training_data])

            st.session_state.model.fit(X_train, y_train)
            st.success("✅ Model retrained with user feedback!")
