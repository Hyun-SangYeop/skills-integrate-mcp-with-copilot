# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Teachers can sign up and unregister students after logging in
- Students can view activities and participant lists without an account

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Create a teacher account (the command prompts for a password and stores only its hash):

   ```
   python create_teacher.py
   ```

3. Run the application from the `src` directory:

   ```
   uvicorn app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| GET    | `/auth/session`                                                   | Get the current teacher login state                                 |
| POST   | `/auth/login`                                                     | Log in with a teacher username and password                         |
| POST   | `/auth/logout`                                                    | Log out the current teacher                                         |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student signup                                         |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only unregister                                      |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activity data is stored in memory and resets when the server restarts. Teacher password hashes are stored in the untracked `teachers.json` file. Set `SESSION_SECRET` to a stable, random value when deploying; without it, active sessions expire when the server restarts. Set `COOKIE_SECURE=true` when serving over HTTPS.
