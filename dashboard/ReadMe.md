# Brent Oil Price Analysis Dashboard

Interactive dashboard for visualizing Brent oil price analysis, change point detection, and historical event correlations.

## Features

- **Interactive Price Charts**: Visualize Brent oil prices from 1987-2022
- **Event Correlation**: See how historical events correlate with price changes
- **Change Point Analysis**: View detected structural breaks in price patterns
- **Impact Quantification**: Measure the impact of events on oil prices
- **Filtering & Drill-down**: Filter by date range, event type, and severity
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Architecture

The dashboard consists of two main components:

1. **Backend (Flask API)**: Serves historical data, analysis results, and statistical metrics
2. **Frontend (React)**: Interactive user interface with visualizations

## Prerequisites

- Python 3.9+ with pip
- Node.js 16+ with npm
- Git

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd dashboard/backend
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate

3. Install dependencies:

   ```bash
   pip install -r requirements.txt

### Frontend Setup
1. Navigate to the frontend directory:

    ```bash
    cd ../frontend
2. Install dependencies:

   ```bash
   npm install

# Running the Application

Option 1: Development Mode (Separate Processes)
1. Start the backend server:

   ```bash
   cd backend
   python app.py

Backend will run at: http://localhost:5000

2. In a new terminal, start the frontend:

   ```bash
    cd frontend
    npm start
Frontend will run at: http://localhost:3000

Option 2: Docker (Recommended for Production)
1. Build and run with Docker Compose:

   ```bash
   docker-compose up --build
2. Access the dashboard at: http://localhost:3000

# API Endpoints
The backend provides the following REST API endpoints:

GET /api/prices - Historical price data
GET /api/events - Historical events
GET /api/change-points - Detected change points
GET /api/impact - Impact analysis results
GET /api/stats - Summary statistics
GET /api/volatility - Volatility metrics
GET /api/event-impact/<date> - Price data around specific event

# Project Structure
text
dashboard/
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Docker configuration
│   └── run.py            # Run script
├── frontend/
│   ├── public/            # Static files
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── App.css       # Styles
│   │   ├── index.js      # Entry point
│   │   └── index.css     # Global styles
│   ├── package.json      # Node.js dependencies
│   └── README.md         # Frontend documentation
├── docker-compose.yml    # Docker orchestration
└── README.md 

# Data Sources
The dashboard uses data from the following sources:

1. Brent Oil Prices: Daily prices from 1987-2022
2. Historical Events: Manually researched geopolitical and economic events
3. Analysis Results: Output from Bayesian change point models

# Usage Guide
1. Price Analysis Tab
- View the full price history
- See event markers on the timeline
- Identify change points (vertical dashed lines)

2. Events & Impact Tab
- Filter events by type and severity
- View events distribution by type and severity
- See impact analysis charts

3. Change Points Tab
- View detected change point details
- See confidence intervals (95% HDI)
- Read impact summaries

4. Volatility Tab
- View volatility metrics
- Monitor market stability indicators

5. Statistics Tab
- View dataset statistics
- Check data quality metrics

# Troubleshooting

Common Issues
1. Backend not connecting:
- Ensure Flask server is running on port 5000
- Check that all data files are in the correct location

2. Frontend not loading:
- Clear browser cache
- Check console for errors
- Ensure all dependencies are installed

3. Missing data:

- Run the Task 2 analysis notebook first
- Check file paths in the backend

# Error Messages
- "Failed to fetch data": Backend server may not be running
- "Data not available": Required data files may be missing
- "CORS error": Ensure CORS is enabled in the backend

# Deployment
# Production Deployment
1. Build the frontend:

   ```bash
   cd frontend
   npm run build

2. Configure the backend to serve static files:

- Copy the build folder to backend/static
- Update Flask app to serve the frontend

3. Use a production WSGI server:

   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

# Cloud Deployment Options
- AWS: Elastic Beanstalk or EC2 with RDS
- Azure: App Service with Azure SQL
- Google Cloud: App Engine with Cloud SQL
- Heroku: Simple deployment with Postgres

# Development
# Adding New Features

1. New API Endpoint:
- Add route in backend/app.py
- Update frontend to call the new endpoint

2. New Visualization:
- Add new React component
- Import Recharts or other charting library
- Add to appropriate tab

3. New Filter:

- Add filter option in App.js
- Update API calls to include new parameter
- Update backend to handle new filter

# Code Standards

- Use consistent naming conventions
- Add comments for complex logic
- Follow PEP 8 for Python code
- Follow ESLint rules for JavaScript
- Write unit tests for new functionality

# Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

# License
This project is part of the KAIM Academy assignment. All rights reserved.

# Contact
For questions or issues, please contact:
- Project Lead: [Biniyam Mitiku]
- Email: [binattamit@gmail.com]

# Acknowledgments
- KAIM Academy for the project requirements
- All open-source libraries used in this project