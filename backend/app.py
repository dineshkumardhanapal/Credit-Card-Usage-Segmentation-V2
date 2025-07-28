# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Define the path to your clustered CSV file
# Make sure 'clustered_credit_card_data.csv' is in the same directory as app.py
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
    # Use 0.0.0.0 for host to make it accessible from outside the container in Render
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))

