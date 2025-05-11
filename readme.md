# Car Detailing Management System

A comprehensive web application for managing a car detailing business, built with Flask and MySQL.

## Features

- **User Authentication**
  - Secure login and registration system
  - Role-based access control (admin/customer)
  - Password hashing for security

- **Customer Management**
  - Customer profiles with contact information
  - Service history tracking
  - Vehicle management for each customer

- **Vehicle Management**
  - Track multiple vehicles per customer
  - Store vehicle details (make, model, year, color, license plate)

- **Service Management**
  - Define and manage detailing services
  - Set pricing and service duration
  - Service descriptions

- **Appointment Scheduling**
  - Book appointments for specific vehicles and services
  - Calendar view for appointments
  - Status tracking (scheduled, completed, cancelled)

- **Admin Dashboard**
  - Overview of daily appointments
  - Customer and service statistics
  - Manage customers, vehicles, services, and appointments

## Technical Stack

- **Backend**: Python Flask
- **Database**: MySQL (via PyMySQL)
- **Frontend**: HTML, CSS, JavaScript (templates not included in this repository)
- **Authentication**: Session-based with password hashing

## Installation

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/car-detailing-management.git
   cd car-detailing-management
   ```

2. **Set up a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install flask pymysql
   ```

4. **Set up the database**
   - Create a MySQL database named `car_detailing_db`
   - Import the database schema (see Database Schema section)

5. **Run the application**
   ```
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Database Schema

The application requires the following MySQL tables:

- **customers**: Store customer information
- **users**: User authentication data linked to customers
- **vehicles**: Vehicle information linked to customers
- **services**: Available detailing services
- **appointments**: Scheduled appointments linking customers, vehicles, and services

You can create these tables using the following SQL:

```sql
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    customer_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT,
    license_plate VARCHAR(20),
    color VARCHAR(30),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration INT NOT NULL COMMENT 'Duration in minutes'
);

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    service_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    notes TEXT,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT
);
```

## Default Admin Account

The system has a default admin account:
- Email: admin@admin.com
- Password: admin123 

## Usage

### Admin Features
- Log in as an admin
- Access the dashboard to view daily appointments
- Manage customers, vehicles, services, and appointments
- View service history for customers

### Customer Features
- Register as a new customer
- Add vehicles to your profile
- Schedule appointments for your vehicles
- View and manage your service history
- Update your profile information

## Security Notes

- The application uses SHA-256 for password hashing
- For production use, consider implementing:
  - HTTPS
  - More secure password hashing (e.g., bcrypt)
  - CSRF protection
  - Rate limiting for login attempts

## Contributors

- AutoWash

## Acknowledgements

- Flask framework
- PyMySQL
- XAMPP for local development