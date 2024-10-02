# Bookmark App

## Overview

This project is a Flask-based web application that uses several extensions to provide a robust and scalable backend. The application includes database management, JWT-based authentication, CORS support, and background scheduling.

## Features

- **Flask**: The core web framework.
- **Flask-SQLAlchemy**: SQLAlchemy support for database operations.
- **Flask-Migrate**: Database migrations using Alembic.
- **Flask-JWT-Extended**: JWT-based authentication.
- **Flask-CORS**: Cross-Origin Resource Sharing support.
- **APScheduler**: Background scheduling for periodic tasks.
- **BeautifulSoup4 (bs4)**: For web scraping and parsing HTML/XML documents.
- **os**: For interacting with the operating system.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-repo/project-name.git
    cd project-name
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the environment variables:
    ```sh
        SECRET_KEY = 'YOUR SECRET KEY'
        JWT_SECRET_KEY = 'YOUR SECRET KEY'
    ```

5. Configure the database in app/config.py



