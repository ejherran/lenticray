# # Lenticray

Lenticray is an advanced analysis and prediction system for algae proliferation in freshwater bodies. It uses a combination of fuzzy logic and neural networks to analyze datasets related to water variables, determine the trophic level, and provide insights and forecasts about the state of the water body. The system is designed for researchers, environmental managers, and anyone interested in understanding and managing freshwater ecosystems.

## Table of Contents

- [Project Structure](#project-structure)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

The Lenticray system is organized into three main packages:

1. **`ia`**: Contains all the necessary components for fuzzy logic processes and neural networks.
2. **`back`**: The backend of the project, built with [FastAPI](https://fastapi.tiangolo.com/).
3. **`front`**: The frontend of the project, built with [ReactJS](https://reactjs.org/).

### Detailed Overview

- **`ia/`**: This package implements the logic for analyzing datasets using fuzzy logic and training neural network models for time series predictions. It serves as the core analytical engine of the system.
- **`back/`**: This package serves as the API server using FastAPI. It handles API requests, manages user authentication, dataset management, and orchestrates communication between the analytical engine (`ia`) and the frontend.
- **`front/`**: This package is the user interface of the system, providing an intuitive way to interact with the platform. It allows users to define projects, upload datasets, configure studies, and visualize results and predictions.

## System Requirements

To run the Lenticray system, the following services are required:

1. **Nginx**: Used as a web server to serve the frontend and manage requests.
2. **Redis**: Used for queue management, handling background tasks and asynchronous operations.
3. **SQLite**: Used as the primary database for storing user data, projects, datasets, and studies.
4. **Python 3.11**: Required to run the backend server and analytical engine.
5. **Node.js 20.18 and npm 10.8**: Required to build and run the frontend.