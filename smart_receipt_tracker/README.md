# Smart Receipt Tracker

AI-powered receipt processing using Azure Document Intelligence.

## Features

- Single and bulk receipt processing
- Automatic data extraction (merchant, total, date, items)
- CSV export for bulk results
- Real-time Azure Document Intelligence integration

## Tech Stack

- Python Flask backend
- Azure Document Intelligence API
- HTML/CSS/JavaScript frontend

## Setup

Set environment variables:
```bash
DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint
DOCUMENT_INTELLIGENCE_KEY=your_key
```

Run:
```bash
pip install -r requirements.txt
python app.py
```

## Usage

Navigate to `/smart-receipt-tracker` and upload receipt images.
