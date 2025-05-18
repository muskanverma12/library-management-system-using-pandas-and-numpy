from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd  
import numpy as np   
from io import BytesIO

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    book_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Student:'{self.name}', email:'{self.email}', course:'{self.course}', address:'{self.address}', phone:'{self.phone}', book_name:'{self.book_name}'"

with app.app_context():
    if not os.path.exists('library_database.db'):
        db.create_all()

@app.route('/')
def home():
    student_home = Student.query.all()
    return render_template('home.html', student_home=student_home)

@app.route('/add/student', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        course = request.form.get('course')
        address = request.form.get('address')
        phone = request.form.get('phone')
        book_name = request.form.get('book_name')

        new_student = Student(name=name, email=email, course=course, address=address, phone=phone, book_name=book_name)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_student.html')

@app.route('/update/student/<int:student_id>', methods=['GET', 'POST'])
def update(student_id):
    student_edit = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student_edit.name = request.form['name']
        student_edit.email = request.form['email']
        student_edit.course = request.form['course']
        student_edit.address = request.form['address']
        student_edit.phone = request.form['phone']
        student_edit.book_name = request.form['book_name']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('update_student.html', student=student_edit)

@app.route('/delete/student/<int:student_id>', methods=['GET', 'POST'])
def delete(student_id):
    student_delete = Student.query.get_or_404(student_id)
    db.session.delete(student_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/export/students')
def export_students():
    students = Student.query.all()
    data = [{
        "ID": s.id,
        "Name": s.name,
        "Email": s.email,
        "Course": s.course,
        "Address": s.address,
        "Phone": s.phone,
        "Book Name": s.book_name
    } for s in students]

    df = pd.DataFrame(data)
    
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(output, download_name="students_data.csv", as_attachment=True)

@app.route('/stats/phone_length')
def phone_length_stats():
    students = Student.query.all()
    phone_lengths = np.array([len(s.phone) for s in students])

    if phone_lengths.size == 0:
        avg_length = 0
    else:
        avg_length = np.mean(phone_lengths)

    return f"Average phone number length: {avg_length:.2f} digits."

if __name__ == "__main__":
    app.run(debug=True, port=5001)
