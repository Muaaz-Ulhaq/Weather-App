# Weather App

A comprehensive weather application that provides current weather data, 5-day forecasts, and an AI-powered summary for any location worldwide. The application features a user-friendly interface built with Streamlit and is powered by a robust FastAPI backend.

## Features

-   **Current Weather:** Get real-time weather information for any city, ZIP code, or GPS coordinate.
-   **5-Day Forecast:** View a detailed 5-day forecast with temperature trends visualized in a graph.
-   **Custom Date Range:** Select a specific date range within the next 5 days to see aggregated forecast data.
-   **AI Weather Summary:** Generate a human-readable weather summary and recommendations using Google's Gemini AI.
-   **Search History:** Automatically save your weather searches to a persistent history log.
-   **History Management:** View, refresh, delete, and export your saved weather history records to CSV.
-   **Automatic Location Detection:** The app can automatically detect and load the weather for your current city on startup.
-   **AI City Name Correction:** Automatically corrects typos in city names to ensure accurate search results.
-   **Dual Unit Support:** Switch between Celsius/metric and Fahrenheit/imperial units.

## Architecture

The project is split into two main components: a backend REST API and a frontend web application.

### Backend

*   **Framework:** **FastAPI** provides a robust and high-performance API server, and **Google Gemini API** generates intelligent weather summaries.
*   **Data Source:** Weather data is fetched from the **OpenWeatherMap API**.
*   **Database:** A **SQLite** database (`weather_app.db`) is used to store weather history records.
*   **Functionality:** Exposes endpoints for fetching current weather, forecasts, and performing CRUD (Create, Read, Update, Delete) operations on the history data.

### Frontend

*   **Framework:** **Streamlit** is used to create an interactive, multi-page web application.
*   **Pages:**
    *   **Current Weather & Forecast:** The main page for searching and displaying weather information.
    *   **Weather History:** A separate page for managing saved history records.
*   **Visualization:** **Plotly** is used to render interactive line charts for temperature trends.
*   **API Communication:** The `requests` library is used to communicate with the backend FastAPI service.

## Tech Stack

*   **Backend:** Python, FastAPI, Pydantic, SQLite, python-dotenv
*   **Frontend:** Streamlit, Plotly, Requests
*   **Core:** Python 3

## Setup and Installation

Follow these steps to run the Weather App locally.

### 1. Prerequisites

*   Python 3.8 or newer
*   `pip` package installer

### 2. Clone the Repository

```bash
git clone https://github.com/Muaaz-Ulhaq/Weather-App.git
cd Weather-App
```

### 3. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

You need an API key from [OpenWeatherMap](https://openweathermap.org/api) to fetch weather data.

1.  Create a file named `.env` in the root directory of the project.
2.  Add your OpenWeatherMap API key to the `.env` file in the following format:

    ```
    OPENWEATHER_API_KEY=your_actual_api_key_here
    ```

### 5. Run the Application

The application requires two separate processes: one for the backend and one for the frontend.

**A. Start the Backend Server**

Open a terminal and run the following command to start the FastAPI server. The `--reload` flag enables hot-reloading for development.

```bash
uvicorn backend.main_api:app --reload
```

The backend API will be available at `http://127.0.0.1:8000`. You can view the auto-generated API documentation at `http://127.0.0.1:8000/docs`.

**B. Start the Frontend Application**

Open a second terminal and run the following command to launch the Streamlit app.

```bash
streamlit run frontend/Current_Weather.py
```

Your web browser should automatically open a new tab with the Weather App running.

## Project Structure

```
.
├── backend/                  # Contains the FastAPI backend application
│   ├── config.py             # Configuration and environment variables
│   ├── db_service.py         # SQLite database interaction logic
│   ├── main_api.py           # FastAPI endpoints definition
│   ├── models.py             # Pydantic data models
│   ├── utils.py              # Utility functions (e.g., location parsing)
│   └── weather_api.py        # Wrapper for OpenWeatherMap API calls
├── frontend/                 # Contains the Streamlit frontend application
│   ├── Current_Weather.py    # Main Streamlit page
│   ├── api_client.py         # Functions to call the backend API
│   ├── config.py             # Frontend configuration
│   └── pages/                # Additional Streamlit pages
│       └── Weather_History.py
├── .env                      # (You need to create this) API keys and secrets
├── requirements.txt          # Project dependencies
└── weather_app.db            # SQLite database file
