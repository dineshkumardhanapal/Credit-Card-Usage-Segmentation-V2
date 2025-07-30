#!/bin/bash

# Navigate to the application root directory where app.py and requirements.txt are located
# On Azure App Service, the repository content is usually deployed to /home/site/wwwroot
cd /home/site/wwwroot

# Create and activate a virtual environment if it doesn't exist
# This ensures dependencies are installed in a controlled environment
if [ ! -d "antenv" ]; then
    echo "Creating virtual environment 'antenv'..."
    python3.10 -m venv antenv
fi

echo "Activating virtual environment 'antenv'..."
source antenv/bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the Gunicorn server
echo "Starting Gunicorn server..."
# The app:app refers to the 'app' Flask instance within the 'app.py' file
gunicorn --bind 0.0.0.0 --timeout 600 app:app

# Keep the script running to prevent the container from exiting
# This is important for Azure App Service to keep the process alive
tail -f /dev/null
