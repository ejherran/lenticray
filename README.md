# # Lenticray

Lenticray is an advanced analysis and prediction system for algae proliferation in freshwater bodies. It uses a combination of fuzzy logic and neural networks to analyze datasets related to water variables, determine the trophic level, and provide insights and forecasts about the state of the water body. The system is designed for researchers, environmental managers, and anyone interested in understanding and managing freshwater ecosystems.

## Table of Contents

- [Project Structure](#project-structure)
- [System Requirements](#system-requirements)

## Project Structure

The Lenticray system is organized into three main packages:

1. **`ia`**: Contains all the necessary components for fuzzy logic processes and neural networks.
2. **`back`**: The backend of the project, built with [FastAPI](https://fastapi.tiangolo.com/).
3. **`front`**: The frontend of the project, built with [ReactJS](https://reactjs.org/).

### Detailed Overview

- **`ia/`**: This package implements the logic for analyzing datasets using fuzzy logic and training neural network models for time series predictions. It serves as the core analytical engine of the system.
- **`back/`**: This package serves as the API server using FastAPI. It handles API requests, manages user authentication, dataset management, and orchestrates communication between the analytical engine (`ia`) and the frontend.
- **`front/`**: This package is the user interface of the system, providing an intuitive way to interact with the platform. It allows users to define projects, upload datasets, configure studies, and visualize results and predictions.
- **`research/`**: This directory contains the notebooks, datasets and inference plots used in the research base to create this platform.  For academic interest only. 

## System Requirements

To run the Lenticray system, the following services are required:

1. **Nginx**: Used as a web server to serve the frontend and manage requests.
2. **Redis**: Used for queue management, handling background tasks and asynchronous operations.
3. **SQLite**: Used as the primary database for storing user data, projects, datasets, and studies.
4. **Python 3.11**: Required to run the backend server and analytical engine.
5. **Pyenv**: Necessary to manage Python versions and dependencies.
6. **Node.js 20.18 and npm 10.8**: Required to build and run the frontend.

## Installation

Follow these steps to install the Lenticray system:

### 1. Clone the Repository

First, clone the Lenticray repository:

```bash
git clone git@github.com:ejherran/lenticray.git
```

### 2. Install System Requirements

For Debian-based systems, you can install the necessary services using the following commands:

```bash
# Install Nginx
sudo apt-get install nginx

# Install Redis
sudo apt-get install redis-server

# Install SQLite
sudo apt-get install sqlite3

# Install Python 3, pip and build essentials
sudo apt install python3-pip python3-dev build-essential python3-setuptools

# Install pyenv (for Python version management)
sudo apt install pipenv

# Install Node.js and npm
sudo apt-get install nodejs npm
```

Optionally, you can install `certbot` to manage SSL certificates for Nginx. Please refer to the [Certbot official documentation](https://certbot.eff.org) for more information.

### 3. Install Python Dependencies

Navigate to the backend directory and set up the Python environment:

```bash
cd lenticray
pipenv shell        # Activate the virtual environment
pipenv sync         # Install all Python dependencies
```

### 4. Install Node.js Dependencies

Navigate to the frontend directory and install the required Node.js packages:

```bash
cd ../front
npm ci              # Install all Node.js dependencies with a clean install
```

### 5. Start the Backend Server

Navigate to the backend directory and start the FastAPI server:

```bash
cd ../back
cp .env_template .env  # Copy the environment template file and update it with the necessary configurations
uvicorn main:app --reload  # Start the backend server in development mode
```

### 6. Start the Frontend Server

Navigate to the frontend directory and start the React development server:

```bash
cd ../front
cp .env_template .env  # Copy the environment template file and update it with the necessary configurations
HOST=localhost PORT=3000 npm run start  # Start the frontend server
```

### 7. Start IA Service

```bash
python run_ai.py
```

NOTE: The IA service is a standalone service that can be run independently from the backend and frontend. It is responsible for training neural networks and performing fuzzy logic analysis.

This service use the redis server to comunicate with the backend and manage the queue of tasks.

You can run the IA service in background using the following command:

```bash
nohup python run_ai.py &
```

or you can use the `supervisord` a tool like `tmux` to run the service and detach the terminal.

### 8. Access the System

Once both servers are running, you can access the system by opening your browser and navigating to:

```
http://localhost:3000
```

### 8. Optional: Setup Nginx and systemd Services

You can use the configuration files in the `system_files` directory to set up Nginx and systemd services for both the backend and frontend, enabling them to run as system services. This setup will allow the services to automatically start on system boot.

For more information on how to configure these services, refer to the files provided in the `system_files` directory.

**Note:** To serve the frontend in production mode, you need to install `serve` globally:

```bash
npm install -g serve
```

Then, you can use `serve` to serve the frontend build:

```bash
serve -s build
```