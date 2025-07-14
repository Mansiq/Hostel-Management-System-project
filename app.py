from flask import Flask, render_template, request, redirect, url_for,flash

app = Flask(__name__)
app.secret_key = 'm123'
students_data = [] 
rooms_data = [] 

@app.route('/')
def dashboard():
    total_students = len(students_data)
    total_rooms = len(rooms_data)
    return render_template('index.html',
                           total_students=total_students,
                           total_rooms=total_rooms)

@app.route('/students')
def student_list():
    return render_template('students.html', students=students_data)

@app.route('/rooms')
def room_list():
    return render_template('rooms.html', rooms=rooms_data)

# Add Student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        room_no = request.form['room_no']

        # Check room capacity
        for room in rooms_data:
            if room['room_no'] == room_no:
                if room['occupied'] >= room['capacity']:
                    flash(f"Room {room_no} is already full. Please choose a different room.", "danger")
                    return redirect(url_for('add_student'))
                else:
                    room['occupied'] += 1
                    break
        else:
            # Room doesn't exist, create with default capacity
            rooms_data.append({
                "room_no": room_no,
                "capacity": 2,
                "occupied": 1
            })

        new_id = len(students_data) + 1
        students_data.append({
            "id": new_id,
            "name": name,
            "email": email,
            "room": room_no
        })
        return redirect(url_for('student_list'))

    return render_template('add_student.html')

# Add Room
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_no = request.form['room_no']
        capacity = int(request.form['capacity'])  # FIXED: convert to int

        # Check if room already exists
        for room in rooms_data:
            if room['room_no'] == room_no:
                # Optional: flash a message or update existing room
                return redirect(url_for('room_list'))

        rooms_data.append({
            "room_no": room_no,
            "capacity": capacity,
            "occupied": 0
        })
        return redirect(url_for('room_list'))
    return render_template('add_room.html')
@app.route('/update_student')
def show_update_form():
    return render_template('update_student.html')

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    # Later: Delete from DB
    flash('Student has been deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
