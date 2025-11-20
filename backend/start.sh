#!/bin/bash
echo "Starting EcomImagePro Backend..."
uvicorn app.main:app --reload --port 8000

