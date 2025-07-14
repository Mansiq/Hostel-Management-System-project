
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'm123'

def get_db_connection():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create students table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            room_no VARCHAR(10) NOT NULL
        )
    ''')
    
    # Create rooms table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_no VARCHAR(10) PRIMARY KEY,
            capacity INTEGER NOT NULL,
            occupied INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT COUNT(*) FROM students')
    total_students = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM rooms')
    total_rooms = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return render_template('index.html',
                           total_students=total_students,
                           total_rooms=total_rooms)

@app.route('/students')
def student_list():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT id, name, email, room_no FROM students ORDER BY id')
    students = cur.fetchall()
    
    students_data = []
    for student in students:
        students_data.append({
            'id': student[0],
            'name': student[1],
            'email': student[2],
            'room': student[3]
        })
    
    cur.close()
    conn.close()
    
    return render_template('students.html', students=students_data)

@app.route('/rooms')
def room_list():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT room_no, capacity, occupied FROM rooms ORDER BY room_no')
    rooms = cur.fetchall()
    
    rooms_data = []
    for room in rooms:
        rooms_data.append({
            'room_no': room[0],
            'capacity': room[1],
            'occupied': room[2]
        })
    
    cur.close()
    conn.close()
    
    return render_template('rooms.html', rooms=rooms_data)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        room_no = request.form['room_no']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if room exists and has capacity
        cur.execute('SELECT capacity, occupied FROM rooms WHERE room_no = %s', (room_no,))
        room = cur.fetchone()
        
        if room:
            capacity, occupied = room
            if occupied >= capacity:
                flash(f"Room {room_no} is already full. Please choose a different room.", "danger")
                cur.close()
                conn.close()
                return redirect(url_for('add_student'))
            else:
                # Update room occupancy
                cur.execute('UPDATE rooms SET occupied = occupied + 1 WHERE room_no = %s', (room_no,))
        else:
            # Create room with default capacity
            cur.execute('INSERT INTO rooms (room_no, capacity, occupied) VALUES (%s, %s, %s)', 
                       (room_no, 2, 1))
        
        # Add student
        try:
            cur.execute('INSERT INTO students (name, email, room_no) VALUES (%s, %s, %s)', 
                       (name, email, room_no))
            conn.commit()
            flash("Student added successfully!", "success")
        except psycopg2.IntegrityError:
            flash("A student with this email already exists!", "danger")
            conn.rollback()
        
        cur.close()
        conn.close()
        return redirect(url_for('student_list'))

    return render_template('add_student.html')

@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_no = request.form['room_no']
        capacity = int(request.form['capacity'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('INSERT INTO rooms (room_no, capacity, occupied) VALUES (%s, %s, %s)', 
                       (room_no, capacity, 0))
            conn.commit()
            flash("Room added successfully!", "success")
        except psycopg2.IntegrityError:
            flash("Room already exists!", "danger")
            conn.rollback()
        
        cur.close()
        conn.close()
        return redirect(url_for('room_list'))
    
    return render_template('add_room.html')

@app.route('/update_student')
def show_update_form():
    return render_template('update_student.html')

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get student's room to update occupancy
    cur.execute('SELECT room_no FROM students WHERE id = %s', (student_id,))
    result = cur.fetchone()
    
    if result:
        room_no = result[0]
        # Delete student
        cur.execute('DELETE FROM students WHERE id = %s', (student_id,))
        # Update room occupancy
        cur.execute('UPDATE rooms SET occupied = occupied - 1 WHERE room_no = %s AND occupied > 0', (room_no,))
        conn.commit()
        flash('Student has been deleted successfully!', 'success')
    else:
        flash('Student not found!', 'danger')
    
    cur.close()
    conn.close()
    return redirect(url_for('student_list'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)
