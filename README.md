# Health Check Application (Team A)

This is a web-based platform designed to record and visualize software product development operations using Spotify's Health Check technique.

## About the Project

Health Check is a technique used to assess the health of teams. Engineering teams discuss and rate the health of critical areas in the team's operations (Code Base Health, Testing, Release Processes, Stakeholder Relations, etc.).

This application is designed to record, visualize, and track the progress of teams' health status over time.

## Requirements

To run this project, you need the following software and libraries:

- Python 3.8 or newer
- Django 5.1.6
- Other Python libraries (listed in the requirements.txt file)

## Installation

### 1. Install Python

You can download the latest version of Python from [python.org](https://www.python.org/downloads/).

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Libraries

```bash
pip install -r requirements.txt
```

If the requirements.txt file doesn't exist, you can install the necessary libraries with the following command:

```bash
pip install django==5.1.6
```

### 4. Create the Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

### 6. Create a Directory for Static Files

```bash
mkdir static
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

## Usage

After starting the development server, you can access the following URLs:

- Home Page: `http://127.0.0.1:8000/`
- Admin Panel: `http://127.0.0.1:8000/admin/`
- Health Cards: `http://127.0.0.1:8000/healthcards/` or `http://127.0.0.1:8000/teamhealth/`

## Project Structure

The project consists of two main applications:

1. **accounts**: User management, authentication, and team management
2. **healthcards**: Health cards, sessions, votes, and team summaries

## Features

- User Registration and Authentication
- Team Management
- Creating and Editing Health Cards
- Session Management
- Voting on Health Cards
- Team Summaries and Visualization
- Tracking Progress Over Time
- Team Comparison

## Command Reference

### Database Operations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset the database (use with caution!)
python manage.py flush
```

### User Management

```bash
# Create a superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword <username>
```

### Development Tools

```bash
# Start Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Start the development server
python manage.py runserver

# Start the server on a specific port
python manage.py runserver 8080
```

### Testing

```bash
# Run all tests
python manage.py test

# Run tests for a specific application
python manage.py test accounts
```

## Troubleshooting

### Database Errors

If you encounter database-related errors, try the following steps:

1. Recreate and apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. If that doesn't work, reset the database (be careful, all data will be deleted):
   ```bash
   python manage.py flush
   ```

### Static File Errors

If you encounter errors related to static files:

1. Make sure the `static` directory exists:
   ```bash
   mkdir static
   ```

2. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

## License

This project is licensed under the [MIT License](LICENSE). 