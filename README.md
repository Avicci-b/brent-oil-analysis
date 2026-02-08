# brent-oil-analysis
An analysis made for Birhan Energy
# Brent Oil Price Analysis - Change Point Detection

## Project Overview
This project analyzes Brent crude oil prices from 1987-2022 to identify structural breaks caused by geopolitical events, OPEC decisions, and economic shocks using Bayesian change point detection.

## Project Structure
brent-oil-analysis/
├── data/ # Data storage
├── notebooks/ # Jupyter notebooks for analysis
├── src/ # Source code modules
├── dashboard/ # Interactive dashboard
├── reports/ # Interim and final reports
├── docs/ # Documentation
├── tests/ # Test files
├── models/ # Saved models
└── config/ # Configuration files

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+ (for dashboard frontend)
- Git

### Installation

1. Clone the repository:

git clone <https://github.com/Avicci-b/brent-oil-analysis.git>
cd brent-oil-analysis

2. Create and activate virtual environments

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Python dependencies:

pip install -r requirements.txt

4. For dashboard development:

# Backend (Flask)
cd dashboard/backend
pip install -r requirements.txt

# Frontend (React)
cd ../frontend
npm install


## Project Phases
Phase 1 (Interim): Task 1 - Foundation and planning
Phase 2 (Final): Tasks 2 & 3 - Modeling and dashboard development

## Data Sources
Brent oil prices: Historical daily prices (1987-2022)
Historical events: Manually researched geopolitical/economic events

## Key Technologies
- Python (PyMC, pandas, numpy)
- Bayesian Statistics
- Flask (backend API)
- React (frontend dashboard)
- Git & GitHub

