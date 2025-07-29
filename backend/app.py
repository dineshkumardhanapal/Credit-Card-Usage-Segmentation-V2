# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
# CORS will be configured on Azure App Service, but it's good practice to have it here too
# for local development or if Azure's CORS isn't fully configured.
# We will explicitly allow the Render frontend URL on Azure App Service.
CORS(app)

# Define the path to your clustered CSV file
# On Azure App Service, files are typically deployed relative to the application root.
# The `os.path.dirname(__file__)` will point to the directory containing app.py (i.e., 'backend/')
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'clustered_credit_card_data.csv')

@app.route('/api/customer_data', methods=['GET'])
def get_customer_data():
    try:
        # Load the clustered data from CSV
        df_clustered = pd.read_csv(DATA_FILE_PATH)

        # Ensure 'PC1', 'PC2', and 'Cluster' columns exist
        # These columns should have been added by your Python script (from the updated guide)
        required_cols = ['PC1', 'PC2', 'Cluster']
        if not all(col in df_clustered.columns for col in required_cols):
            return jsonify({"error": "Missing required columns (PC1, PC2, Cluster) in CSV. Please ensure your Python script adds them."}), 500

        # Convert the DataFrame to a list of dictionaries (JSON format)
        # We convert all columns to dictionary, the frontend will pick what to display
        data_for_frontend = df_clustered.to_dict(orient='records')

        return jsonify(data_for_frontend)

    except FileNotFoundError:
        return jsonify({"error": f"Data file not found at {DATA_FILE_PATH}. Please ensure 'clustered_credit_card_data.csv' is in the backend directory."}), 404
    except Exception as e:
        # Log the error for debugging on the server side
        app.logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    # This block is for local development only.
    # Azure App Service will use Gunicorn to run the app.
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
