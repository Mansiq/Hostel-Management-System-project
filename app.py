from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'm123'

# In-memory storage (data will be lost when app restarts)
students = []
rooms = []
student_id_counter = 1

@app.route('/')
def dashboard():
    total_students = len(students)
    total_rooms = len(rooms)

    return render_template('index.html',
                           total_students=total_students,
                           total_rooms=total_rooms)

@app.route('/students')
def student_list():
    return render_template('students.html', students=students)

@app.route('/rooms')
def room_list():
    return render_template('rooms.html', rooms=rooms)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    global student_id_counter

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        room_no = request.form['room_no']

        # Check if email already exists
        for student in students:
            if student['email'] == email:
                flash("A student with this email already exists!", "danger")
                return redirect(url_for('add_student'))

        # Check if room exists and has capacity
        room_found = False
        for room in rooms:
            if room['room_no'] == room_no:
                room_found = True
                if room['occupied'] >= room['capacity']:
                    flash(f"Room {room_no} is already full. Please choose a different room.", "danger")
                    return redirect(url_for('add_student'))
                else:
                    room['occupied'] += 1
                break

        if not room_found:
            # Create room with default capacity
            rooms.append({
                'room_no': room_no,
                'capacity': 2,
                'occupied': 1
            })

        # Add student
        students.append({
            'id': student_id_counter,
            'name': name,
            'email': email,
            'room': room_no
        })
        student_id_counter += 1

        flash("Student added successfully!", "success")
        return redirect(url_for('student_list'))

    return render_template('add_student.html')

@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_no = request.form['room_no']
        capacity = int(request.form['capacity'])

        # Check if room already exists
        for room in rooms:
            if room['room_no'] == room_no:
                flash("Room already exists!", "danger")
                return redirect(url_for('add_room'))

        rooms.append({
            'room_no': room_no,
            'capacity': capacity,
            'occupied': 0
        })

        flash("Room added successfully!", "success")
        return redirect(url_for('room_list'))

    return render_template('add_room.html')

@app.route('/update_student')
def show_update_form():
    return render_template('update_student.html')

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    global students, rooms

    # Find and remove student
    student_to_remove = None
    for i, student in enumerate(students):
        if student['id'] == student_id:
            student_to_remove = students.pop(i)
            break

    if student_to_remove:
        # Update room occupancy
        room_no = student_to_remove['room']
        for room in rooms:
            if room['room_no'] == room_no and room['occupied'] > 0:
                room['occupied'] -= 1
                break

        flash('Student has been deleted successfully!', 'success')
    else:
        flash('Student not found!', 'danger')

    return redirect(url_for('student_list'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)