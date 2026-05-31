# Makao Yetu — Full Stack Final Project
### ReactJS + Flask REST API + MySQL
**Developed by: [Your Name] | 2026**

---

## Project Overview

**Makao Yetu** ("Our Homes" in Swahili) is a full-stack property listing and rental platform
connecting house seekers in urban Kenya with verified property agents and landlords.

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | ReactJS, React Router DOM           |
| Backend    | Python Flask, Flask-CORS, Flask-JWT |
| Database   | MySQL (via PyMySQL)                 |
| Auth       | JWT (JSON Web Tokens)               |
| Passwords  | Werkzeug PBKDF2-SHA256 hashing      |
| Images     | Multipart form upload (Flask)       |

---

## Database Design (3 Tables)

### 1. `users`
| Column     | Type         | Notes                    |
|------------|--------------|--------------------------|
| id         | INT PK AI    | Primary key              |
| username   | VARCHAR(80)  | Display name             |
| email      | VARCHAR(120) | Unique, used for login   |
| password   | VARCHAR(256) | Hashed with Werkzeug     |
| phone      | VARCHAR(20)  | M-Pesa phone number      |
| role       | ENUM         | user / agent / admin     |
| created_at | DATETIME     | Auto-set on insert       |

### 2. `properties`
| Column       | Type          | Notes                        |
|--------------|---------------|------------------------------|
| id           | INT PK AI     | Primary key                  |
| title        | VARCHAR(150)  | e.g. "3-Bedroom in Kilimani" |
| location     | VARCHAR(120)  | e.g. "Westlands, Nairobi"    |
| price        | DECIMAL(15,2) | Monthly rent or sale price   |
| prop_type    | ENUM          | rent / sale / land           |
| bedrooms     | INT           | Number of bedrooms           |
| bathrooms    | INT           | Number of bathrooms          |
| description  | TEXT          | Full property description    |
| image        | VARCHAR(255)  | Uploaded filename            |
| user_id      | INT FK        | References users.id          |
| is_available | TINYINT(1)    | 1 = available                |
| created_at   | DATETIME      | Auto-set on insert           |

### 3. `bookings`
| Column         | Type          | Notes                        |
|----------------|---------------|------------------------------|
| id             | INT PK AI     | Primary key                  |
| user_id        | INT FK        | References users.id          |
| property_id    | INT FK        | References properties.id     |
| amount         | DECIMAL(15,2) | Booking/deposit amount       |
| phone          | VARCHAR(20)   | M-Pesa phone                 |
| payment_method | ENUM          | mpesa / card / cash          |
| mpesa_ref      | VARCHAR(30)   | Simulated M-Pesa reference   |
| status         | ENUM          | pending / confirmed / cancel |
| created_at     | DATETIME      | Auto-set on insert           |

---

## API Endpoints

| Method | Endpoint                  | Auth Required | Description              |
|--------|---------------------------|---------------|--------------------------|
| POST   | /api/signup               | No            | Register a new user      |
| POST   | /api/signin               | No            | Login, returns JWT token |
| GET    | /api/get_properties       | No            | List all properties      |
| GET    | /api/get_property/<id>    | No            | Get single property      |
| POST   | /api/add_property         | Yes (JWT)     | List a new property      |
| POST   | /api/book_property        | Yes (JWT)     | Book/purchase a property |
| GET    | /api/my_bookings          | Yes (JWT)     | User's booking history   |
| GET    | /uploads/<filename>       | No            | Serve uploaded images    |

---

## React Pages / Components

| File                  | Route           | Description                          |
|-----------------------|-----------------|--------------------------------------|
| MakaoYetu.jsx         | /               | Home: hero, listings, how it works   |
| Signup.jsx            | /signup         | Registration form                    |
| Signin.jsx            | /signin         | Login form                           |
| AddProperty.jsx       | /add-property   | List a new property (protected)      |
| PropertyDetail.jsx    | /property/:id   | Single listing + booking/payment     |
| MyBookings.jsx        | /my-bookings    | User's transaction history           |

---

## Setup Instructions

### Step 1 — Database
```sql
-- In phpMyAdmin or MySQL CLI:
mysql -u root -p < makao_yetu.sql
```

### Step 2 — Flask Backend
```bash
cd makao_yetu_backend
pip install -r requirements.txt
# Edit DB_CONFIG in app.py if needed (password, host)
python app.py
# Flask runs on http://localhost:5000
```

### Step 3 — React Frontend
```bash
cd makao_yetu_frontend
npm install
npm install react-router-dom
npm start
# React runs on http://localhost:3000
```

---

## Features Implemented

### ✅ User Authentication
- Register with username, email, phone, password
- Passwords hashed with PBKDF2-SHA256 (Werkzeug)
- JWT tokens (7-day expiry) stored in localStorage
- Protected routes redirect unauthenticated users to /signin

### ✅ Property Management
- Add property with title, location, price, type, bedrooms, bathrooms, description
- Image upload (JPG/PNG/WEBP) stored server-side
- View all properties (with type/location filtering)
- View single property with full agent details

### ✅ Transaction / Payment Feature
- M-Pesa simulated payment (generates a real-format reference code e.g. MKY3A7F2E1B)
- Booking confirmation stored in database with status tracking
- My Bookings page shows full transaction history
- Supports M-Pesa, Card, and Cash payment methods

### ✅ UI / Creativity
- Warm Kenyan aesthetic (terracotta, cream, forest green palette)
- Playfair Display + Outfit typography pairing
- Skeleton loading cards while API fetches data
- Sticky navbar with auth-aware state
- Mobile responsive layout

---

## Marking Guide (Self-Assessment)

| Category                  | Max  | Notes                                         |
|---------------------------|------|-----------------------------------------------|
| Backend API Functionality | 30   | 7 endpoints, JWT auth, image upload, booking  |
| React Frontend            | 30   | 6 pages, React Router, fetch API integration  |
| Database Design           | 15   | 3 tables with FKs, seed data, normalized      |
| System Integration        | 15   | Frontend ↔ Flask ↔ MySQL fully connected      |
| UI / Creativity           | 10   | Custom design, animations, Kenyan branding    |
| **TOTAL**                 | 100  |                                               |

---

*Makao Yetu — Our Homes © 2026*
