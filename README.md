# Flights Project

This repository contains a complete data engineering project focused on analyzing flight data from New York City in 2023. It includes everything from data processing and SQL queries to interactive visualizations and dashboards built using Python.

The main part of the project is a Streamlit-based dashboard that lets users explore flight trends, delay patterns, airport traffic, and weather impacts. In addition to the dashboard, the repo also includes raw data files, database schemas, analysis scripts, and supporting files used throughout the project.

**Live Dashboard**: [Launch Dashboard](https://dataengeneering-cdoypn3wy8fwvobqjvuftw.streamlit.app)  

---

## What's Inside

- `dashboardnyc.py`: Main Streamlit application
- `flights_database.db`: SQLite database with joined flight, weather, and airport data
- `airports.csv`: Airport metadata with codes and coordinates
- SQL queries and data wrangling logic (in-code)
- Notebooks and additional scripts (depending on the branch)
- Clean layout for deployment and local development

---

## Features

### Overview Page
- Total flights, flight duration, and distance metrics
- Flight distribution by carrier and airport
- Delay statistics with detailed breakdowns

### Flight Route Statistics
- Select origin and destination to view route performance
- Analyze delay averages by carrier
- View top destinations and interactive airport maps

### Delay Analysis
- Visualize the impact of wind, temperature, and precipitation
- Track hourly delay trends

### Time-Based Statistics
- Choose any date in 2023 and explore:
  - Number of flights
  - Hourly departure/arrival patterns
  - Delay trends and airtime distribution

---

## Technologies Used

- **Python 3.9**
- **Streamlit** for the interactive dashboard
- **SQLite** for querying the data
- **Pandas** and **NumPy** for data wrangling
- **Plotly**, **Altair**, **Seaborn**, and **Matplotlib** for visualizations

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` for installing dependencies

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/beauvantrojen/DataEngeneering.git
   cd DataEngeneering
