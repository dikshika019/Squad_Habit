# 🏆 Squad Habit

Squad Habit is a **habit tracking and accountability application** built with **FastAPI**. It allows users to create and manage squads, build healthy habits, track progress, compete through leaderboards, and identify members who may be at risk of losing consistency.

The project focuses on building consistent habits through **social accountability, team-based challenges, and progress tracking**.

---

## 🚀 Features

### 🔐 Authentication

* User registration and login
* Secure password handling
* JWT-based authentication
* Google OAuth authentication
* Protected routes and user sessions

### 👥 Squad Management

* Create and manage squads
* Join squads using invitation links
* Invite members to squads
* Track squad members
* Manage squad-based habit activities

### ✅ Habit Tracking

* Create and manage habits
* Track daily habit completion
* Monitor individual progress
* Track consistency over time

### 🏆 Leaderboard

* Rank squad members based on habit progress
* Compare member consistency
* Encourage healthy competition and accountability

### ⚠️ At-Risk Tracking

* Identify users who are losing habit consistency
* Monitor missed habit activities
* Help squads encourage members who may need additional motivation

### 🔗 Invitation System

* Generate squad invitation links
* Share invite links with users
* Expire invitation links after a defined period
* Allow users to join squads through invitations

---

## 🛠️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **Pydantic**
* **Pydantic Settings**
* **Uvicorn**

### Authentication & Security

* **JWT**
* **OAuth 2.0 / Google OAuth**
* **Passlib**
* **bcrypt**

### Database

* **SQLite**
* **SQLAlchemy ORM**

### Frontend / UI

* **HTML**
* **Jinja2 Templates**
* CSS

### Configuration

* **Python dotenv**
* Environment variables using `.env`

---

## 📁 Project Structure

```text
Squad_Habit/
│
├── middleware/
│   └── ...
│
├── routes/
│   ├── auth
│   ├── habits
│   ├── squads
│   ├── leaderboard
│   ├── at_risk
│   └── pages
│
├── services/
│   └── ...
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── habits.html
│   ├── leaderboard.html
│   └── at_risk.html
│
├── auth.py
├── config.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── services.py
├── test_flows.py
├── requirements.txt
├── .env
└── .gitignore
```

---

## 🏗️ Application Architecture

The application follows a modular FastAPI structure:

```text
Client
   │
   ▼
FastAPI Routes
   │
   ▼
Services / Business Logic
   │
   ▼
SQLAlchemy Models
   │
   ▼
SQLite Database
```

Authentication and authorization are handled through dedicated authentication logic and middleware, while configuration values are managed through environment variables.

---

## 🔐 Authentication Flow

The application supports authentication using JWT and Google OAuth.

### JWT Authentication

```text
User Login
    ↓
Validate Credentials
    ↓
Generate Access Token
    ↓
Client Stores Token
    ↓
Protected API Request
    ↓
Validate Token
    ↓
Access Protected Resource
```

### Google OAuth

Users can authenticate using Google OAuth, allowing them to sign in without creating a separate password-based account.

---

## 👥 Squad Workflow

A typical squad workflow looks like this:

```text
User
  ↓
Create Squad
  ↓
Generate Invitation Link
  ↓
Share Invite
  ↓
New User Joins Squad
  ↓
Members Track Habits
  ↓
Progress is Recorded
  ↓
Leaderboard is Updated
```

---

## 🔗 Invitation System

Squad Habit includes an invitation system that allows users to invite others to join their squads.

The invitation workflow includes:

* Generate a unique invitation token
* Create an invitation link
* Set an expiration time
* Validate the invitation
* Allow users to join the squad
* Prevent expired invitations from being used

---

## 📊 Habit & Progress Tracking

Users can track their habits and monitor their consistency.

The application can be used to:

* Create personal habits
* Mark habits as completed
* Monitor progress
* Maintain consistency
* Compare progress with squad members

This makes the application suitable for building accountability through group participation.

---

## 🏆 Leaderboard

The leaderboard provides a ranking system for squad members.

It helps users:

* Compare their progress
* Stay motivated
* Maintain consistency
* Compete in a healthy way

The leaderboard encourages users to actively participate in their habits and remain consistent.

---

## ⚠️ At-Risk Members

The At-Risk feature helps identify members who may be losing consistency.

The system can monitor habit activity and highlight members who:

* Miss multiple habit activities
* Show reduced consistency
* May need additional motivation

This allows squad members to support each other and improve accountability.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dikshika019/Squad_Habit.git
```

Navigate to the project directory:

```bash
cd Squad_Habit
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Example configuration:

```env
DATABASE_URL=sqlite:///./sql_app.db

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

FRONTEND_URL=http://localhost:3000

INVITE_EXPIRY_HOURS=24
```

> Never commit your real `.env` file or secret credentials to GitHub.

---

### 5. Run the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## 📚 API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

These interfaces can be used to explore and test the available API endpoints.

---

## 🧪 Testing

The project includes a `test_flows.py` file for testing application flows.

Tests can be run using:

```bash
pytest
```

---

## 🔮 Future Improvements

Potential improvements for the project include:

* PostgreSQL database integration
* Redis-based caching
* Background task processing
* Email notifications for missed habits
* Push notifications
* Advanced habit analytics
* Weekly and monthly progress reports
* More detailed squad statistics
* Docker support
* Automated CI/CD pipeline
* Comprehensive automated test coverage

---

## 🎯 Learning Outcomes

This project helped practice and demonstrate:

* FastAPI application structure
* REST API development
* JWT authentication
* Google OAuth integration
* SQLAlchemy ORM
* Database relationships
* Pydantic schemas
* Environment-based configuration
* Middleware
* Modular routing
* Service-layer architecture
* Jinja2 template integration
* Invitation and token-based workflows
* Habit tracking logic
* Leaderboard implementation
* Deployment and production configuration

---

