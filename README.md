# NYC Flights Dashboard

This project is an interactive dashboard that helps you explore and understand flight activity from New York City airports in 2023. Using real data and visualizations, it shows how flights are distributed across time, carriers, routes, and weather conditions.

Built with Python and Streamlit, it combines data engineering, analysis, and visualization in a clean and easy-to-use web app.

**Live App**: [Launch Dashboard](https://dataengeneering-cdoypn3wy8fwvobqjvuftw.streamlit.app)  
**GitHub Repo**: [View Repository](https://github.com/beauvantrojen/DataEngeneering)

---

## What You’ll Find in the Dashboard

The dashboard is divided into four main sections:

### 1. Overview
- Total number of flights
- Average flight duration and distance
- Flight distribution across airports and airlines
- Summary of departure and arrival delays

### 2. Flight Route Statistics
- Select any departure and arrival airport
- See flight counts and average delays per carrier
- View maps of airports and routes
- Top destinations from a selected airport

### 3. Delay Analysis
- Explore how weather (wind, temperature, and rain) affects delays
- Understand delay patterns throughout the day

### 4. Time-Based Statistics
- Choose a date in 2023 and view all flights that day
- Airport activity by hour (arrivals and departures)
- Average departure delays by hour
- Distribution of airtime

---

## Technologies Used

- **Python 3.9**
- **Streamlit** for the interactive dashboard
- **SQLite** for querying the data
- **Pandas** and **NumPy** for data wrangling
- **Plotly**, **Altair**, **Seaborn**, and **Matplotlib** for visualizations

---

## Data Source

All the data used in this project comes from a cleaned and preprocessed SQLite database: `flights_database.db`.  
It includes three main datasets:
- `flights`: Flight departure/arrival times, delays, distance, etc.
- `weather`: Wind speed, temperature, and precipitation
- `airports`: Metadata including airport names, IATA codes, and coordinates

These were compiled and filtered for flights departing from New York City in 2023.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/beauvantrojen/DataEngeneering.git
   cd DataEngeneering
