# A simple ToDo list using SQLite as db by P. Hernandez

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor, CKEditorField

# from dotenv import load_dotenv

# Flask app instantiation & Flask connect to DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task-list'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'

ckeditor = CKEditor(app)

db = SQLAlchemy(app)


#  Create Tables -- Task_Table  --

class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), unique=True)
    task_detail = db.Column(db.Text(500))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)


# create a task form model  with Flask-WTForm

class TaskForm(FlaskForm):
    id = IntegerField('id')
    task_name = StringField("Task_Name", validators=[DataRequired()])
    category = StringField("Category")
    task_detail = CKEditorField("Task_Detail")
    start_date = DateField('start_date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('end_date', format='%Y-%m-%d', validators=[DataRequired()])
    status = StringField("Task_Status", validators=[DataRequired()])
    submit = SubmitField("Submit Task")


# Decorator Functions

@app.route('/', methods=['GET', 'POST'])
def home():
    all_tasks = Task.query.all()
    if request.method == "POST":
        if request.form.get('button') == 'Insert Tasks':
            return render_template("form.html")
        elif request.form.get('button') == 'View Tasks':
            return render_template('view.html', all_tasks=all_tasks)
        elif request.form.get('button') == "Delete Task":
            return render_template('delete.html')
    return render_template('home.html')


@app.route("/view", methods=['GET', 'POST'])
def task():
    all_tasks = Task.query.all()
    return render_template('view.html', all_tasks=all_tasks, title='all tasks')


@app.route("/show_task/<int:id>")
def show_task(id):
    task = Task.query.filter_by(id=id).first_or_404("There is no record")
    return render_template('show_task.html', task=task, task_id=id)


@app.route('/add_task', methods=["GET", "POST"])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            task_name=form.task_name.data,
            category=form.category.data,
            task_detail=form.task_detail.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("task"))
    else:
        return render_template('form.html', title='add section', form=form)


@app.route('/delete/<int:id>')
def delete_task(id):
    task_to_delete = Task.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/view')
    except:
        return "There was an error deleting that record"


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    task_to_update = Task.query.get_or_404(id)
    form = TaskForm(obj=task_to_update)
    if form.validate_on_submit():
        form.populate_obj(obj=task_to_update)
        db.session.commit()
        return redirect(url_for('task'))
    return render_template('form.html', form=form, task_id=id, title="edit section")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
