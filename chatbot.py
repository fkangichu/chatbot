from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import fields, ValidationError
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, join
import os, datetime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chatbot.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

class Visitor(db.Model):
    __tablename__ = 'Visitor'
    id = db.Column(db.Integer, primary_key=True)
    nationalID = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    company = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text(), nullable=True)

class Department(db.Model):
    __tablename__ = 'Department'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), index=True, unique=False, nullable=False)
    # employees = db.relationship('Employee', backref='department', lazy='dynamic')
       
class Title(db.Model):
    __tablename__ = 'Title'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    # employees = db.relationship('Employee', backref='title', lazy='dynamic')

class Employee(db.Model):
    __tablename__ = 'Employee'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('Department.id'))
    department = db.relationship('Department', backref=db.backref('departments', lazy='dynamic'),)
    title_id = db.Column(db.Integer, db.ForeignKey('Title.id'))
    title = db.relationship('Title', backref=db.backref('titles', lazy='dynamic'),)

class Meetings(db.Model): 
    __tablename__ = 'Meetings'
    meeting_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('Visitor.id'))
    visitor = db.relationship('Visitor', backref='visitorID')
    employee_id = db.Column(db.Integer, db.ForeignKey('Employee.id'))
    employee = db.relationship('Employee', backref='employeeID')
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class VisitorSchema(ma.Schema):
    class Meta:
        fields = ('nationalID', 'name', 'email', 'phone', 'company', 'message')

visitor_schema = VisitorSchema()
visitors_schema = VisitorSchema(many=True)

class DepartmentSchema(ma.Schema):
    class Meta:
        fields = ('name',)

department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)

class TitleSchema(ma.Schema):
    class Meta:
        fields = ('name',)

title_schema = TitleSchema()
titles_schema = TitleSchema(many=True)

class EmployeeSchema(ma.Schema):
    class Meta:
        fields = ('name', 'email', 'department', 'title')
            
    departmentID = ma.Nested(DepartmentSchema)
    titleID = ma.Nested(TitleSchema)

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True, only=('name', 'email'))

class MeetingsSchema(ma.Schema):
    class Meta:
        fields = ('meeting_id', 'visitor', 'employee', 'date', 'time')
  
    visitorID = ma.Nested(VisitorSchema)
    employeeID = ma.Nested(EmployeeSchema)

meeting_schema = MeetingsSchema()
meetings_schema = MeetingsSchema(many=True)

# add visitor
@app.route("/visitor", methods=["POST"])
def add_visitor():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    
    # Validate and deserialize input
    try:
        data = visitor_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    visitor = Visitor(
        nationalID = data['nationalID'],
        name = data['name'],
        email = data['email'],
        phone = data['phone'],
        company = data['company'],
        message = data['message'],
        )
    
    db.session.add(visitor)
    db.session.commit()
    # result = visitor_schema.dump(Visitor.query.get(id))

    return jsonify({
        'message': 'New visitor added',
    })

#show all visitors
@app.route("/visitor", methods=["GET"])
def get_visitor():
    all_visitors = Visitor.query.all()
    result = visitors_schema.dump(all_visitors)
    return jsonify({'all_visitors': result})

#show visitor by id
@app.route("/visitor/<int:id>")
def visitor_detail(id):
    try:
        visitor = Visitor.query.get(id)
    except IntegrityError:
        return jsonify({'message': 'Visitor could not be found.'}), 400
    result = visitor_schema.dump(visitor)
    return jsonify({'visitor': result})

#add department
@app.route("/department", methods=["POST"])
def add_department():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    
    # Validate and deserialize input
    try:
        data = department_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    department = Department(
        name = data['name'],
        )
    
    db.session.add(department)
    db.session.commit()

    return jsonify({
        'message': 'New department added',
    })

#show all departments
@app.route("/department", methods=["GET"])
def get_department():
    all_departments = Department.query.all()
    result = departments_schema.dump(all_departments)
    return jsonify({'all_departments':result})

#show department by id and employees in that department
@app.route("/department/<int:id>")
def department_detail(id):
    try:
        department = Department.query.get(id)
    except IntegrityError:
        return jsonify({'message': 'Department could not be found.'}), 400

    department_result = department_schema.dump(department)
    employee_result = employees_schema.dump(department.departments.all())

    return jsonify({
        'department': department_result,
        'employees': employee_result})

#add title
@app.route("/title", methods=["POST"])
def add_title():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    
    # Validate and deserialize input
    try:
        data = title_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    title = Title(
        name = data['name'],
        )
    
    db.session.add(title)
    db.session.commit()

    return jsonify({
        'message': 'New title added',
    })

#show all titles 
@app.route("/title", methods=["GET"])
def get_title():
    all_titles = Title.query.all()
    result = titles_schema.dump(all_titles)
    return jsonify(result)

#add employee
@app.route("/employee", methods=["POST"])
def add_employee():
    json_data = request.get_json()
    print(json_data)
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    data = employee_schema.load(json_data)
    print(data)
    
    # Validate and deserialize input
    try:
        data = employee_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    departmentID = Department.query.filter_by(id=data['department']).first()
    titleID = Title.query.filter_by(id=data['title']).first()
    
    employee = Employee(
        name = data['name'],
        email = data['email'],
        department = departmentID,
        title = titleID,
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify({
        'message': 'New employee added',
    })

#show all employees
@app.route("/employee", methods=["GET"])
def get_employee():
    all_employees = Employee.query.all()
    result = employees_schema.dump(all_employees)
    return jsonify(result)

#show all employees with their departments
@app.route("/employees/all", methods=["GET"])
def all_employees():
    try:
        employees = (db.session.query(Employee.name, Department.name, Title.name).join(Department).join(Title)).all()
    except IntegrityError:
        return jsonify({'message': 'Invalid.'}), 400

    return jsonify({'All employees': employees})

#show employee by id
@app.route("/employee/<int:id>")
def employee_detail(id):
    try:
        employee = (db.session.query(Employee.name, Employee.email, Department.name, Title.name).join(Department).join(Title).filter(Employee.id==id)).all()
    except IntegrityError:
        return jsonify({'message': 'Employee could not be found.'}), 400
    
    return jsonify({'employee': employee})

#add meeting
@app.route("/meeting", methods=["POST"])
def add_meeting():
    json_data = request.get_json()
    print(json_data)
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    data = employee_schema.load(json_data)
    
    # Validate and deserialize input
    try:
        data = meeting_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    visitorID = Visitor.query.filter_by(id=data['visitor']).first()
    employeeID = Employee.query.filter_by(id=data['employee']).first()
    
    meeting = Meetings(
        visitor = visitorID,
        employee = employeeID,
        date = data['date'],
        time = data['timr'],
    )

    db.session.add(meetings_schema)
    db.session.commit()

    return jsonify({
        'message': 'New meeting added',
    })

#show all meetings
@app.route("/meetings", methods=["GET"])
def get_visit():
    all_meetings = Meetings.query.all()
    result = meetings_schema.dump(all_meetings)
    return jsonify(result)

#show meeting by meeting_id
@app.route("/meetings/<int:meeting_id>")
def meeting_detail(meeting_id):
    try:
        meeting = (db.session.query(Meetings.meeting_id, Employee.name, Visitor.name, Meetings.date, Meetings.time).join(Employee).join(Visitor).filter(Meetings.meeting_id==meeting_id)).all()
    except IntegrityError:
        return jsonify({'message': 'Meeting ID could not be found.'}), 400
    
    return jsonify({'meeting': meeting})

#endpoint to mark a meeting that has taken place


if __name__ == '__main__':
    app.run(debug=True, port=5000)