# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import joblib # Import joblib to load the models

app = Flask(__name__)
CORS(app)

# Define paths to the original raw data and the saved models
ORIGINAL_DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'credit_card_data.csv')
SCALER_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'scaler_model.joblib')
PCA_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'pca_model.joblib')
DBSCAN_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'dbscan_model.joblib')

# Load models and original data globally when the app starts
# This avoids reloading them on every request, improving performance
try:
    original_df = pd.read_csv(ORIGINAL_DATA_FILE_PATH)
    # Handle missing values as done during training
    original_df.fillna(original_df.mean(numeric_only=True), inplace=True)

    scaler = joblib.load(SCALER_MODEL_PATH)
    pca = joblib.load(PCA_MODEL_PATH)
    dbscan = joblib.load(DBSCAN_MODEL_PATH)
    app.logger.info("ML Models and original data loaded successfully.")
except FileNotFoundError as e:
    app.logger.error(f"Required file not found: {e}. Ensure all data and model files are in the root directory.")
    # Exit or raise an error to prevent the app from starting incorrectly
    raise SystemExit(f"Startup failed: {e}")
except Exception as e:
    app.logger.error(f"Error loading ML models or original data: {e}", exc_info=True)
    raise SystemExit(f"Startup failed due to ML model/data loading error: {e}")


@app.route('/api/customer_data', methods=['GET'])
def get_customer_data():
    try:
        # Perform preprocessing and clustering on demand
        # We use the globally loaded original_df and models
        features = original_df.drop('CUST_ID', axis=1) # Assuming 'CUST_ID' is your customer identifier

        scaled_features = scaler.transform(features)
        pca_components = pca.transform(scaled_features)
        clusters = dbscan.fit_predict(pca_components)

        # Create a DataFrame for the frontend response
        df_response = original_df.copy()
        df_response['PC1'] = pca_components[:, 0]
        df_response['PC2'] = pca_components[:, 1]
        df_response['Cluster'] = clusters

        # Convert the DataFrame to a list of dictionaries (JSON format)
        data_for_frontend = df_response.to_dict(orient='records')

        return jsonify(data_for_frontend)

    except Exception as e:
        app.logger.error(f"Error during data processing or API response: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred during data processing.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
