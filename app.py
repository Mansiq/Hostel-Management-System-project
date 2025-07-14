from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'm123'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hostel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.String(10), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    occupied = db.Column(db.Integer, default=0)

    def has_space(self):
        return self.occupied < self.capacity


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    room_no = db.Column(db.String(10), db.ForeignKey('room.room_no'), nullable=False)


# Create tables if not exist
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/')
def dashboard():
    total_students = Student.query.count()
    total_rooms = Room.query.count()
    return render_template('index.html', total_students=total_students, total_rooms=total_rooms)


@app.route('/students')
def student_list():
    students = Student.query.all()
    return render_template('students.html', students=students)


@app.route('/rooms')
def room_list():
    rooms = Room.query.all()
    return render_template('rooms.html', rooms=rooms)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        room_no = request.form['room_no']

        if Student.query.filter_by(email=email).first():
            flash("A student with this email already exists!", "danger")
            return redirect(url_for('add_student'))

        room = Room.query.filter_by(room_no=room_no).first()

        if room:
            if not room.has_space():
                flash(f"Room {room_no} is already full. Please choose a different room.", "danger")
                return redirect(url_for('add_student'))
            room.occupied += 1
        else:
            # Create new room with default capacity if not exists
            room = Room(room_no=room_no, capacity=2, occupied=1)
            db.session.add(room)

        student = Student(name=name, email=email, room_no=room_no)
        db.session.add(student)
        db.session.commit()

        flash("Student added successfully!", "success")
        return redirect(url_for('student_list'))

    return render_template('add_student.html')


@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_no = request.form['room_no']
        capacity = int(request.form['capacity'])

        if Room.query.filter_by(room_no=room_no).first():
            flash("Room already exists!", "danger")
            return redirect(url_for('add_room'))

        room = Room(room_no=room_no, capacity=capacity)
        db.session.add(room)
        db.session.commit()

        flash("Room added successfully!", "success")
        return redirect(url_for('room_list'))

    return render_template('add_room.html')


@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        room = Room.query.filter_by(room_no=student.room_no).first()
        if room and room.occupied > 0:
            room.occupied -= 1
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted successfully!", "success")
    else:
        flash("Student not found!", "danger")
    return redirect(url_for('student_list'))

@app.route('/update_student')
def show_update_form():
    flash("Update feature coming soon!", "info")
    return redirect(url_for('student_list'))


# --- Run App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
