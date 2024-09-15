import os
from flask import render_template, flash, redirect, url_for
from app import app
from flask import request, jsonify
from urllib.parse import urlsplit
from app.forms import LoginForm, TaskForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import db
from app.models import User, Task
from flask_login import logout_user, login_required
from werkzeug.utils import secure_filename
import secrets
from flask import send_file, abort



@app.route('/')
@app.route('/index')
@login_required
def index():
    users = User.query.all()
    tasks = Task.query.order_by(Task.date_created.desc()).all()
    return render_template('index.html',title='Home',tasks=tasks,users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_task', methods=['GET','POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data   
        file = form.file.data
        if file:
            original_filename = file.filename
            file_extension = os.path.splitext(original_filename)[1]
            saved_filename = secrets.token_hex(16) + file_extension
            print(f"File saved to: {os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], saved_filename))

            new_task = Task(title=title, content=content, 
                            user_id=current_user.id,
                            original_filename=original_filename, 
                            saved_filename=saved_filename)
        else:
            new_task = Task(title=title, content=content, user_id=current_user.id)                
        db.session.add(new_task)
        db.session.commit()
        flash('Your task has been added!')
        return redirect(url_for('index'))
    return render_template('add_task.html', title='Add Task', form=form)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.saved_filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], task.saved_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(task)
    db.session.commit()
    flash('Task has been deleted.')
    return redirect(url_for('index'))

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    task = Task.query.get_or_404(file_id)

    if task.saved_filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], task.saved_filename)
        
        print(f"Trying to download file from: {file_path}")

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=task.original_filename)
        else:
            print(f"File not found: {file_path}")
            abort(404, description="File not found.")
    else:
        abort(404, description="No file associated with this task.")

@app.route('/filter_tasks')
@login_required
def filter_tasks():
    user_id = request.args.get('user_id')
    print(f"User ID received: {user_id}")
    if user_id:
        tasks = Task.query.filter_by(user_id=user_id).all()
    else:
        tasks = Task.query.all()
    print(f"Filtered tasks: {tasks}")
    return render_template('task_list_partial.html', tasks=tasks)
