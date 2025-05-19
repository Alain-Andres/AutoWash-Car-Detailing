# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from datetime import datetime
import os
from functools import wraps
import hashlib  # For password hashing

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection function
def get_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Default XAMPP MySQL password is empty
        database='car_detailing_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login decorator for protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Home route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = hash_password(request.form['password'])

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # Check if email already exists in users
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already registered. Please log in.', 'warning')
                    return redirect(url_for('login'))

                # Insert into customers table
                cursor.execute("""
                    INSERT INTO customers (name, email, phone, address, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (name, email, phone, address))
                customer_id = cursor.lastrowid

                # Insert into users table with customer_id
                cursor.execute("""
                    INSERT INTO users (email, password, name, role, customer_id, created_at)
                    VALUES (%s, %s, %s, %s, %s,  NOW())
                """, (email, password, name, 'user', customer_id))
                user_id = cursor.lastrowid

                # Optionally add vehicle
                if request.form.get('make') and request.form.get('model'):
                    make = request.form.get('make') or None
                    model = request.form.get('model') or None
                    year = request.form.get('year') or None
                    license_plate = request.form.get('license_plate') or None
                    color = request.form.get('color') or None
                    # Insert into vehicles table

                    cursor.execute("""
                        INSERT INTO vehicles (customer_id, make, model, year, license_plate, color)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (customer_id, make, model, year, license_plate, color))

                connection.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
        finally:
            connection.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        if email != "admin@admin.com":
            password = hash_password(request.form['password'])
        else:
            password = request.form['password']

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email = %s AND password = %s"
                cursor.execute(sql, (email, password))
                customer = cursor.fetchone()
                
                if customer:
                    session['logged_in'] = True
                    session['customer_id'] = customer['customer_id']
                    session['customer_name'] = customer['name']
                    print(customer['id'])
                    flash('Login successful', 'success')
                    if customer['role'] == 'admin':
                        return redirect(url_for('dashboard'))
                    return redirect(url_for('index'))
                else:
                    flash('Invalid credentials', 'danger')
        finally:
            connection.close()
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Get today's appointments
            today = datetime.now().strftime('%Y-%m-%d')
            sql = """
                SELECT a.*, c.name as customer_name, c.phone, v.make, v.model 
                FROM appointments a
                JOIN customers c ON a.customer_id = c.id
                JOIN vehicles v ON a.vehicle_id = v.id
                WHERE DATE(a.appointment_date) = %s
            """
            cursor.execute(sql, (today,))
            appointments = cursor.fetchall()
            
            # Get services count
            cursor.execute("SELECT COUNT(*) as count FROM services")
            services_count = cursor.fetchone()['count']
            
            # Get customers count
            cursor.execute("SELECT COUNT(*) as count FROM customers")
            customers_count = cursor.fetchone()['count']
            
            # Get upcoming appointments count
            cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE appointment_date >= %s", (today,))
            upcoming_count = cursor.fetchone()['count']
            
        return render_template('admin/dashboard.html', 
                               appointments=appointments,
                               services_count=services_count, 
                               customers_count=customers_count,
                               upcoming_count=upcoming_count)
    finally:
        connection.close()


@app.route('/profile')
@login_required
def profile():
    customer_id = session['customer_id']
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Get customer details
            sql = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(sql, (customer_id,))
            customer = cursor.fetchone()
            
            # Get customer's vehicles
            sql = "SELECT * FROM vehicles WHERE customer_id = %s"
            cursor.execute(sql, (customer_id,))
            vehicles = cursor.fetchall()
            
            # Get customer's service history
            sql = """
                SELECT a.*, s.name as service_name, v.make, v.model 
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                JOIN vehicles v ON a.vehicle_id = v.id
                WHERE a.customer_id = %s
                ORDER BY a.appointment_date DESC
            """
            cursor.execute(sql, (customer_id,))
            service_history = cursor.fetchall()
            
            return render_template('users/profile.html', 
                                  customer=customer, 
                                  vehicles=vehicles,
                                  service_history=service_history)
    finally:
        connection.close()

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    customer_id = session['customer_id']
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                name = request.form['name']
                email = request.form['email']
                phone = request.form['phone']
                address = request.form['address']
                
                # Update customer information
                sql = """UPDATE customers 
                         SET name = %s, email = %s, phone = %s, address = %s 
                         WHERE id = %s"""
                cursor.execute(sql, (name, email, phone, address, customer_id))
                
                # Update password if provided
                if request.form.get('password') and request.form['password'].strip():
                    password = hash_password(request.form['password'])
                    sql = "UPDATE customers SET password = %s WHERE id = %s"
                    cursor.execute(sql, (password, customer_id))
                    
                connection.commit()
                session['customer_name'] = name  # Update session name
                flash('Profile updated successfully', 'success')
                return redirect(url_for('profile'))
            
            # Get customer for edit form
            sql = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(sql, (customer_id,))
            customer = cursor.fetchone()
                
            return render_template('users/profile_edit.html', customer=customer)
    finally:
        connection.close()

# CUSTOMER ROUTES - CREATE, READ, UPDATE, DELETE
@app.route('/customers')
@login_required
def customers():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM customers"
            cursor.execute(sql)
            customers = cursor.fetchall()
        return render_template('admin/customers/index.html', customers=customers)
    finally:
        connection.close()

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (name, email, phone, address))
                connection.commit()
                
                # Get the new customer ID for vehicle registration
                customer_id = cursor.lastrowid
                
                # Add vehicle if provided
                if request.form.get('make') and request.form.get('model'):
                    make = request.form['make']
                    model = request.form['model']
                    year = request.form['year']
                    license_plate = request.form['license_plate']
                    color = request.form['color']
                    
                    sql = """INSERT INTO vehicles 
                             (customer_id, make, model, year, license_plate, color) 
                             VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (customer_id, make, model, year, license_plate, color))
                    connection.commit()
                
                flash('Customer added successfully', 'success')
                return redirect(url_for('customers'))
        except Exception as e:
            flash(f'Error adding customer: {str(e)}', 'danger')
        finally:
            connection.close()
            
    return render_template('admin/customers/add.html')

@app.route('/customers/view/<int:id>')
@login_required
def view_customer(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Get customer details
            sql = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(sql, (id,))
            customer = cursor.fetchone()
            
            if not customer:
                flash('Customer not found', 'danger')
                return redirect(url_for('customers'))
            
            # Get customer's vehicles
            sql = "SELECT * FROM vehicles WHERE customer_id = %s"
            cursor.execute(sql, (id,))
            vehicles = cursor.fetchall()
            
            # Get customer's service history
            sql = """
                SELECT a.*, s.name as service_name, v.make, v.model 
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                JOIN vehicles v ON a.vehicle_id = v.id
                WHERE a.customer_id = %s
                ORDER BY a.appointment_date DESC
            """
            cursor.execute(sql, (id,))
            service_history = cursor.fetchall()
            
            return render_template('admin/customers/view.html', 
                                  customer=customer, 
                                  vehicles=vehicles,
                                  service_history=service_history)
    finally:
        connection.close()

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                name = request.form['name']
                email = request.form['email']
                phone = request.form['phone']
                address = request.form['address']
                
                sql = """UPDATE customers 
                         SET name = %s, email = %s, phone = %s, address = %s 
                         WHERE id = %s"""
                cursor.execute(sql, (name, email, phone, address, id))
                connection.commit()
                
                flash('Customer updated successfully', 'success')
                return redirect(url_for('customers'))
            
            # Get customer for edit form
            sql = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(sql, (id,))
            customer = cursor.fetchone()
            
            if not customer:
                flash('Customer not found', 'danger')
                return redirect(url_for('customers'))
                
            return render_template('admin/customers/edit.html', customer=customer)
    finally:
        connection.close()

@app.route('/customers/delete/<int:id>')
@login_required
def delete_customer(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # First delete related vehicles
            sql = "DELETE FROM vehicles WHERE customer_id = %s"
            cursor.execute(sql, (id,))
            
            # Then delete customer
            sql = "DELETE FROM customers WHERE id = %s"
            cursor.execute(sql, (id,))
            
            connection.commit()
            flash('Customer deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting customer: {str(e)}', 'danger')
    finally:
        connection.close()
        
    return redirect(url_for('customers'))

# VEHICLE ROUTES
@app.route('/vehicles/add/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def add_vehicle(customer_id):
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        license_plate = request.form['license_plate']
        color = request.form['color']
        
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """INSERT INTO vehicles 
                         (customer_id, make, model, year, license_plate, color) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (customer_id, make, model, year, license_plate, color))
                connection.commit()
                
                flash('Vehicle added successfully', 'success')
                return redirect(url_for('view_customer', id=customer_id))
        except Exception as e:
            flash(f'Error adding vehicle: {str(e)}', 'danger')
        finally:
            connection.close()
    
    # Get customer information
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(sql, (customer_id,))
            customer = cursor.fetchone()
            
            if not customer:
                flash('Customer not found', 'danger')
                return redirect(url_for('customers'))
                
            return render_template('admin/vehicles/add.html', customer=customer)
    finally:
        connection.close()

@app.route('/vehicles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                make = request.form['make']
                model = request.form['model']
                year = request.form['year']
                license_plate = request.form['license_plate']
                color = request.form['color']
                
                sql = """UPDATE vehicles 
                         SET make = %s, model = %s, year = %s, 
                             license_plate = %s, color = %s 
                         WHERE id = %s"""
                cursor.execute(sql, (make, model, year, license_plate, color, id))
                connection.commit()
                
                customer_id = request.form['customer_id']
                flash('Vehicle updated successfully', 'success')
                return redirect(url_for('view_customer', id=customer_id))
            
            # Get vehicle for edit form
            sql = """SELECT v.*, c.id as customer_id, c.name as customer_name 
                     FROM vehicles v
                     JOIN customers c ON v.customer_id = c.id
                     WHERE v.id = %s"""
            cursor.execute(sql, (id,))
            vehicle = cursor.fetchone()
            
            if not vehicle:
                flash('Vehicle not found', 'danger')
                return redirect(url_for('customers'))
                
            return render_template('admin/vehicles/edit.html', vehicle=vehicle)
    finally:
        connection.close()
# USER VEHICLE ROUTES

@app.route('/profile/vehicle/add', methods=['GET', 'POST'])
@login_required
def profile_add_vehicle():
    
    customer_id = session['customer_id']
    
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        license_plate = request.form['license_plate']
        color = request.form['color']
        
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # Check if license plate already exists
                sql = "SELECT id FROM vehicles WHERE license_plate = %s AND customer_id != %s"
                cursor.execute(sql, (license_plate, customer_id))
                existing = cursor.fetchone()
                
                if existing:
                    flash('A vehicle with this license plate already exists', 'danger')
                    return redirect(url_for('profile_add_vehicle'))
                
                # Insert new vehicle
                sql = """INSERT INTO vehicles 
                         (customer_id, make, model, year, license_plate, color) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (customer_id, make, model, year, license_plate, color))
                connection.commit()
                
                flash('Vehicle added successfully', 'success')
                return redirect(url_for('profile'))
        except Exception as e:
            flash(f'Error adding vehicle: {str(e)}', 'danger')
        finally:
            connection.close()
    
    # Get customer information for the template
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(sql, (customer_id,))
            customer = cursor.fetchone()
            
            if not customer:
                flash('Customer profile not found', 'danger')
                return redirect(url_for('login'))
                
            return render_template('users/add_vehicle.html', customer=customer)
    finally:
        connection.close()

@app.route('/profile/vehicle/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def profile_edit_vehicle(id):

    customer_id = session['customer_id']
    
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # First verify this vehicle belongs to the logged-in user
            sql = "SELECT * FROM vehicles WHERE id = %s AND customer_id = %s"
            cursor.execute(sql, (id, customer_id))
            vehicle = cursor.fetchone()
            
            if not vehicle:
                flash('Vehicle not found or you do not have permission to edit it', 'danger')
                return redirect(url_for('profile'))
            
            if request.method == 'POST':
                make = request.form['make']
                model = request.form['model']
                year = request.form['year']
                license_plate = request.form['license_plate']
                color = request.form['color']
                
                # Check if license plate already exists (excluding this vehicle)
                sql = "SELECT id FROM vehicles WHERE license_plate = %s AND id != %s"
                cursor.execute(sql, (license_plate, id))
                existing = cursor.fetchone()
                
                if existing:
                    flash('A vehicle with this license plate already exists', 'danger')
                    return redirect(url_for('edit_vehicle', id=id))
                
                # Update the vehicle
                sql = """UPDATE vehicles 
                         SET make = %s, model = %s, year = %s, 
                             license_plate = %s, color = %s 
                         WHERE id = %s AND customer_id = %s"""
                cursor.execute(sql, (make, model, year, license_plate, color, id, customer_id))
                connection.commit()
                
                flash('Vehicle updated successfully', 'success')
                return redirect(url_for('profile'))
                
            return render_template('users/edit_vehicle.html', vehicle=vehicle)
    finally:
        connection.close()

@app.route('/vehicles/delete/<int:id>')
@login_required
def delete_vehicle(id):
    customer_id = session['customer_id']
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verify vehicle belongs to logged-in customer
            sql = "SELECT * FROM vehicles WHERE id = %s AND customer_id = %s"
            cursor.execute(sql, (id, customer_id))
            if not cursor.fetchone():
                flash('Vehicle not found or access denied', 'danger')
                return redirect(url_for('profile'))
            
            # Delete vehicle
            sql = "DELETE FROM vehicles WHERE id = %s AND customer_id = %s"
            cursor.execute(sql, (id, customer_id))
            connection.commit()
            
            flash('Vehicle deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting vehicle: {str(e)}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('profile'))

@app.route('/services/delete/<int:id>')
@login_required
def delete_service(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Check if service is referenced in appointments
            sql = "SELECT COUNT(*) as count FROM appointments WHERE service_id = %s"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                flash('Cannot delete service that has appointments', 'danger')
                return redirect(url_for('services'))
            
            # Delete service
            sql = "DELETE FROM services WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()
            
            flash('Service deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting service: {str(e)}', 'danger')
    finally:
        connection.close()
        
    return redirect(url_for('services'))


@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    customer_id = session['customer_id']
    
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        service_id = request.form['service_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        notes = request.form['notes']
        
        # Combine date and time
        appointment_datetime = f"{appointment_date} {appointment_time}:00"
        
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # Verify vehicle belongs to logged-in customer
                sql = "SELECT * FROM vehicles WHERE id = %s AND customer_id = %s"
                cursor.execute(sql, (vehicle_id, customer_id))
                if not cursor.fetchone():
                    flash('Vehicle not found or access denied', 'danger')
                    return redirect(url_for('schedule_appointment'))
                
                sql = """INSERT INTO appointments 
                         (customer_id, vehicle_id, service_id, appointment_date, notes, status) 
                         VALUES (%s, %s, %s, %s, %s, 'scheduled')"""
                cursor.execute(sql, (customer_id, vehicle_id, service_id, appointment_datetime, notes))
                connection.commit()
                
                flash('Appointment scheduled successfully', 'success')
                return redirect(url_for('profile'))
        except Exception as e:
            flash(f'Error scheduling appointment: {str(e)}', 'danger')
        finally:
            connection.close()
    
    # Get vehicles and services for form
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Get vehicles
            sql = "SELECT id, make, model, license_plate FROM vehicles WHERE customer_id = %s"
            cursor.execute(sql, (customer_id,))
            vehicles = cursor.fetchall()
            
            # Get services
            sql = "SELECT id, name, description, price, duration FROM services ORDER BY name"
            cursor.execute(sql)
            services = cursor.fetchall()
            
            return render_template('users/schedule.html', 
                                  vehicles=vehicles, 
                                  services=services)
    finally:
        connection.close()

@app.route('/appointments/cancel/<int:id>')
@login_required
def cancel_appointment(id):
    customer_id = session['customer_id']
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verify appointment belongs to logged-in customer
            sql = "SELECT * FROM appointments WHERE id = %s AND customer_id = %s"
            cursor.execute(sql, (id, customer_id))
            if not cursor.fetchone():
                flash('Appointment not found or access denied', 'danger')
                return redirect(url_for('appointments'))
            
            # Check if appointment is in the past
            sql = """
                SELECT * FROM appointments 
                WHERE id = %s AND appointment_date > NOW()
            """
            cursor.execute(sql, (id,))
            if not cursor.fetchone():
                flash('Cannot cancel past appointments', 'danger')
                return redirect(url_for('profile'))
            
            # Update appointment status
            sql = "UPDATE appointments SET status = 'cancelled' WHERE id = %s AND customer_id = %s"
            cursor.execute(sql, (id, customer_id))
            connection.commit()
            
            flash('Appointment cancelled successfully', 'success')
    except Exception as e:
        flash(f'Error cancelling appointment: {str(e)}', 'danger')
    finally:
        connection.close()
        
    return redirect(url_for('profile'))

@app.route('/appointments/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        vehicle_id = request.form['vehicle_id']
        service_id = request.form['service_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        notes = request.form['notes']
        
        # Combine date and time
        appointment_datetime = f"{appointment_date} {appointment_time}:00"
        
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """INSERT INTO appointments 
                         (customer_id, vehicle_id, service_id, appointment_date, notes, status) 
                         VALUES (%s, %s, %s, %s, %s, 'scheduled')"""
                cursor.execute(sql, (customer_id, vehicle_id, service_id, appointment_datetime, notes))
                connection.commit()
                
                flash('Appointment scheduled successfully', 'success')
                return redirect(url_for('appointments'))
        except Exception as e:
            flash(f'Error scheduling appointment: {str(e)}', 'danger')
        finally:
            connection.close()
    
    # Get customers, vehicles, services for form
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Get customers
            cursor.execute("SELECT id, name FROM customers ORDER BY name")
            customers = cursor.fetchall()
            
            # Get services
            cursor.execute("SELECT id, name, price FROM services ORDER BY name")
            services = cursor.fetchall()
            
            return render_template('admin/appointments/add.html', 
                                  customers=customers, 
                                  services=services)
    finally:
        connection.close()

@app.route('/get_customer_vehicles/<int:customer_id>')
@login_required
def get_customer_vehicles(customer_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, make, model, license_plate FROM vehicles WHERE customer_id = %s"
            cursor.execute(sql, (customer_id,))
            vehicles = cursor.fetchall()
            return {'vehicles': vehicles}
    finally:
        connection.close()

@app.route('/appointments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                service_id = request.form['service_id']
                appointment_date = request.form['appointment_date']
                appointment_time = request.form['appointment_time']
                notes = request.form['notes']
                status = request.form['status']
                
                # Combine date and time
                appointment_datetime = f"{appointment_date} {appointment_time}:00"
                
                sql = """UPDATE appointments 
                         SET service_id = %s, appointment_date = %s, 
                             notes = %s, status = %s 
                         WHERE id = %s"""
                cursor.execute(sql, (service_id, appointment_datetime, notes, status, id))
                connection.commit()
                
                flash('Appointment updated successfully', 'success')
                return redirect(url_for('appointments'))
            
            # Get appointment details
            sql = """
                SELECT a.*, c.name as customer_name, v.make, v.model, v.license_plate
                FROM appointments a
                JOIN customers c ON a.customer_id = c.id
                JOIN vehicles v ON a.vehicle_id = v.id
                WHERE a.id = %s
            """
            cursor.execute(sql, (id,))
            appointment = cursor.fetchone()
            
            if not appointment:
                flash('Appointment not found', 'danger')
                return redirect(url_for('appointments'))
            
            # Format date and time for form
            date_obj = appointment['appointment_date']
            appointment['appt_date'] = date_obj.strftime('%Y-%m-%d')
            appointment['appt_time'] = date_obj.strftime('%H:%M')
            
            # Get services
            cursor.execute("SELECT id, name, price FROM services ORDER BY name")
            services = cursor.fetchall()
            
            return render_template('admin/appointments/edit.html', 
                                  appointment=appointment,
                                  services=services)
    finally:
        connection.close()

@app.route('/appointments/delete/<int:id>')
@login_required
def delete_appointment(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM appointments WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()
            
            flash('Appointment deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting appointment: {str(e)}', 'danger')
    finally:
        connection.close()
        
    return redirect(url_for('appointments'))

@app.route('/services/add', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        duration = request.form['duration']  # in minutes
        
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """INSERT INTO services 
                         (name, description, price, duration) 
                         VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (name, description, price, duration))
                connection.commit()
                
                flash('Service added successfully', 'success')
                return redirect(url_for('services'))
        except Exception as e:
            flash(f'Error adding service: {str(e)}', 'danger')
        finally:
            connection.close()
            
    return render_template('admin/services/add.html')

@app.route('/services/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_service(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                name = request.form['name']
                description = request.form['description']
                price = request.form['price']
                duration = request.form['duration']
                
                sql = """UPDATE services 
                         SET name = %s, description = %s, price = %s, duration = %s 
                         WHERE id = %s"""
                cursor.execute(sql, (name, description, price, duration, id))
                connection.commit()
                
                flash('Service updated successfully', 'success')
                return redirect(url_for('services'))
            
            # Get service for edit form
            sql = "SELECT * FROM services WHERE id = %s"
            cursor.execute(sql, (id,))
            service = cursor.fetchone()
            
            if not service:
                flash('Service not found', 'danger')
                return redirect(url_for('services'))
                
            return render_template('admin/services/edit.html', service=service)
    finally:
        connection.close()
# SERVICE ROUTES
@app.route('/services')
@login_required
def services():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM services"
            cursor.execute(sql)
            services = cursor.fetchall()
        return render_template('admin/services/index.html', services=services)
    finally:
        connection.close()
# APPOINTMENT ROUTES
@app.route('/appointments')
@login_required
def appointments():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT a.*, c.name as customer_name, s.name as service_name,
                       v.make, v.model, v.license_plate
                FROM appointments a
                JOIN customers c ON a.customer_id = c.id
                JOIN services s ON a.service_id = s.id
                JOIN vehicles v ON a.vehicle_id = v.id
                ORDER BY a.appointment_date
            """
            cursor.execute(sql)
            appointments = cursor.fetchall()
        return render_template('admin/appointments/index.html', appointments=appointments)
    finally:
        connection.close()

@app.route('/appointments/complete/<int:id>')
@login_required
def complete_appointment(id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE appointments SET status = 'completed' WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()
            
            flash('Appointment marked as completed', 'success')
    except Exception as e:
        flash(f'Error updating appointment: {str(e)}', 'danger')
    finally:
        connection.close()
        
    return redirect(url_for('appointments'))
if __name__ == '__main__':
    app.run(debug=True)