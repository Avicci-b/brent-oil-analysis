# Data Analysis Workflow - Brent Oil Price Analysis

## Overview
This document outlines the step-by-step workflow for analyzing Brent oil prices using Bayesian change point detection.

## 1. Data Preparation Phase

### 1.1 Data Loading & Inspection
- Load raw CSV data from `data/raw/BrentOilPrices.csv`
- Check data structure and quality
- Identify missing values, duplicates, and outliers

### 1.2 Data Cleaning
- Parse dates in 'day-month-year' format
- Handle missing values (forward fill for time series)
- Remove duplicates
- Validate price values (remove zeros/negatives)

### 1.3 Feature Engineering
- Calculate log returns: `log(price_t) - log(price_{t-1})`
- Create rolling statistics (mean, std, min, max)
- Generate time-based features (year, month, quarter)

## 2. Exploratory Data Analysis (EDA)

### 2.1 Time Series Visualization
- Plot full price history (1987-2022)
- Plot by decades/periods of interest
- Create subplots for different time periods

### 2.2 Statistical Analysis
- Summary statistics (mean, median, std, min, max)
- Distribution analysis (histograms, KDE plots)
- Autocorrelation and partial autocorrelation plots
- Stationarity testing (ADF test, KPSS test)

### 2.3 Volatility Analysis
- Rolling volatility calculation
- Identify periods of high/low volatility
- Analyze volatility clustering patterns

## 3. Historical Event Research

### 3.1 Event Identification
- Research major geopolitical events (2012-2022)
- Identify OPEC decisions and production changes
- Document economic sanctions and trade policies
- Note major economic shocks and crises

### 3.2 Event Database Creation
- Create CSV with: event_date, event_name, event_type, description, expected_impact
- Validate dates align with dataset
- Aim for 15-20 significant events

## 4. Change Point Modeling

### 4.1 Model Selection & Design
- Bayesian change point model using PyMC
- Define priors for change point location (τ)
- Define before/after mean parameters (μ₁, μ₂)
- Implement switch function for regime changes

### 4.2 Model Implementation
- Set up PyMC model with proper likelihood
- Configure MCMC sampling (NUTS algorithm)
- Run multiple chains for convergence checking
- Set appropriate number of samples and tuning steps

### 4.3 Model Diagnostics
- Check convergence (R-hat statistics, trace plots)
- Assess posterior predictive checks
- Evaluate chain mixing and autocorrelation

## 5. Results Interpretation

### 5.1 Change Point Identification
- Analyze posterior distribution of τ
- Identify peaks indicating high probability change points
- Calculate credible intervals for change dates

### 5.2 Impact Quantification
- Compare before/after mean parameters
- Calculate percentage changes
- Assess statistical significance

### 5.3 Event Correlation
- Map detected change points to historical events
- Formulate causal hypotheses
- Assess temporal alignment and plausibility

## 6. Dashboard Development

### 6.1 Backend API Development
- Flask API with endpoints for data retrieval
- Implement data processing pipelines
- Create model prediction endpoints

### 6.2 Frontend Development
- React application with interactive visualizations
- Time series plotting with event overlays
- Filtering and drill-down capabilities

### 6.3 Deployment Preparation
- Docker containerization
- API documentation
- User interface optimization

## 7. Reporting & Communication

### 7.1 Technical Report
- Methodology description
- Results presentation
- Statistical interpretation
- Limitations discussion

### 7.2 Executive Summary
- Key findings for decision-makers
- Actionable insights
- Risk assessment and recommendations

### 7.3 Stakeholder Presentation
- Visual storytelling
- Impact quantification
- Strategic implications

## Tools & Technologies

### Python Libraries
- Data Processing: pandas, numpy
- Visualization: matplotlib, seaborn, plotly
- Modeling: PyMC, scipy, statsmodels
- Dashboard: Flask, React, D3.js

### Development Tools
- Version Control: Git, GitHub
- Environment Management: venv, pip
- Testing: pytest
- Documentation: Markdown, Jupyter

## Quality Assurance

### Validation Steps
- Cross-validate model results
- Sensitivity analysis for parameter choices
- Comparison with alternative methods
- Expert review of event correlations

### Documentation Standards
- Code documentation and comments
- Reproducible notebooks
- Clear variable naming
- Comprehensive README

## Timeline & Milestones

### Phase 1: Foundation
- Data preparation and EDA
- Event research and documentation
- Basic model implementation

### Phase 2: Modeling
- Advanced model development
- Results analysis and interpretation
- Initial dashboard prototype

### Phase 3 : Integration
- Dashboard completion
- Report writing
- Final validation and testing

## Assumptions & Limitations

### Assumptions
1. Market efficiency - prices reflect all available information
2. Events have immediate or short-term lagged effects
3. Change points represent structural breaks
4. Historical events are accurately dated

### Limitations
1. Correlation ≠ causation
2. Model sensitivity to prior specifications
3. Data quality and completeness
4. Simplifying assumptions in model design