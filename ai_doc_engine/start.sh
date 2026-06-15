#!/bin/bash

# Render assigns a dynamic port via the $PORT environment variable.
# If $PORT is set, replace "listen 80;" with "listen $PORT;" in the nginx config.
if [ -n "$PORT" ]; then
    sed -i "s/listen 80;/listen $PORT;/g" /etc/nginx/nginx.conf
fi

echo "🚀 Starting FastAPI Backend on port 8000..."
# Start FastAPI in the background
uvicorn api.main:app --host 127.0.0.1 --port 8000 &

echo "🚀 Starting Streamlit Frontend on port 8501..."
# Start Streamlit in the background
streamlit run ui/app.py --server.port 8501 --server.address 127.0.0.1 &

echo "🚀 Starting Nginx Reverse Proxy..."
# Start Nginx in the foreground to keep the container running
nginx -g "daemon off;"
