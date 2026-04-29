from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db, User, Task, Category, Tag, Subtask, ActivityLog, Reminder, PriorityLevel, RecurrenceType, task_tags
from forms import (
    RegistrationForm, LoginForm, TaskForm, CategoryForm, SubtaskForm, 
    TagForm, SearchForm, FilterForm, ReminderForm, UserPreferencesForm
)
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func
import os

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # ==================== Authentication Routes ====================
    
    @app.route('/')
    def index():
        """Home page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            # Create default categories for new user
            default_categories = [
                Category(name='Work', color='#e74c3c', user_id=user.id),
                Category(name='Personal', color='#9b59b6', user_id=user.id),
                Category(name='Shopping', color='#f39c12', user_id=user.id),
                Category(name='Health', color='#1abc9c', user_id=user.id),
            ]
            db.session.add_all(default_categories)
            db.session.commit()
            
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    # ==================== Dashboard and Task Views ====================
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard"""
        stats = current_user.get_task_stats()
        
        # Get tasks for today
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.due_date >= today_start,
            Task.due_date <= today_end,
            Task.is_completed == False
        ).order_by(Task.priority.desc()).all()
        
        # Get important tasks
        important_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.is_important == True,
            Task.is_completed == False
        ).order_by(Task.due_date).all()
        
        # Get overdue tasks
        overdue_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.due_date < datetime.utcnow(),
            Task.is_completed == False
        ).order_by(Task.due_date).all()
        
        return render_template('dashboard.html', 
                             stats=stats,
                             today_tasks=today_tasks,
                             important_tasks=important_tasks,
                             overdue_tasks=overdue_tasks)
    
    @app.route('/tasks')
    @login_required
    def tasks():
        """View all tasks with filtering and searching"""
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('search', '', type=str)
        priority_filter = request.args.get('priority', '', type=str)
        status_filter = request.args.get('status', '', type=str)
        date_filter = request.args.get('date', '', type=str)
        category_filter = request.args.get('category', '', type=int)
        
        # Base query
        query = Task.query.filter_by(user_id=current_user.id)
        
        # Search filter
        if search_query:
            query = query.filter(or_(
                Task.title.ilike(f'%{search_query}%'),
                Task.description.ilike(f'%{search_query}%')
            ))
        
        # Priority filter
        if priority_filter:
            query = query.filter_by(priority=PriorityLevel[priority_filter.upper()])
        
        # Status filter
        if status_filter == 'completed':
            query = query.filter_by(is_completed=True)
        elif status_filter == 'pending':
            query = query.filter_by(is_completed=False)
        
        # Date filter
        if date_filter:
            today = datetime.utcnow().date()
            if date_filter == 'today':
                start = datetime.combine(today, datetime.min.time())
                end = datetime.combine(today, datetime.max.time())
                query = query.filter(Task.due_date >= start, Task.due_date <= end)
            elif date_filter == 'tomorrow':
                tomorrow = today + timedelta(days=1)
                start = datetime.combine(tomorrow, datetime.min.time())
                end = datetime.combine(tomorrow, datetime.max.time())
                query = query.filter(Task.due_date >= start, Task.due_date <= end)
            elif date_filter == 'overdue':
                query = query.filter(Task.due_date < datetime.utcnow(), Task.is_completed == False)
            elif date_filter == 'this_week':
                week_end = today + timedelta(days=7)
                start = datetime.combine(today, datetime.min.time())
                end = datetime.combine(week_end, datetime.max.time())
                query = query.filter(Task.due_date >= start, Task.due_date <= end)
            elif date_filter == 'this_month':
                month_end = today + timedelta(days=30)
                start = datetime.combine(today, datetime.min.time())
                end = datetime.combine(month_end, datetime.max.time())
                query = query.filter(Task.due_date >= start, Task.due_date <= end)
        
        # Category filter
        if category_filter:
            query = query.filter_by(category_id=category_filter)
        
        # Sorting
        sort_by = request.args.get('sort', 'priority', type=str)
        if sort_by == 'priority':
            query = query.order_by(Task.priority.desc(), Task.due_date)
        elif sort_by == 'date':
            query = query.order_by(Task.due_date)
        elif sort_by == 'recent':
            query = query.order_by(Task.created_at.desc())
        
        # Pagination
        tasks = query.paginate(page=page, per_page=10)
        categories = Category.query.filter_by(user_id=current_user.id).all()
        
        return render_template('tasks.html', 
                             tasks=tasks,
                             categories=categories,
                             search_query=search_query,
                             priority_filter=priority_filter,
                             status_filter=status_filter,
                             date_filter=date_filter,
                             category_filter=category_filter)
    
    @app.route('/task/new', methods=['GET', 'POST'])
    @login_required
    def create_task():
        """Create a new task"""
        form = TaskForm()
        categories = Category.query.filter_by(user_id=current_user.id).all()
        form.category_id.choices = [(-1, 'No Category')] + [(c.id, c.name) for c in categories]
        
        if form.validate_on_submit():
            due_date = None
            if form.due_date.data:
                try:
                    due_date = datetime.fromisoformat(form.due_date.data)
                except:
                    flash('Invalid date format', 'danger')
                    return render_template('create_task.html', form=form)
            
            category_id = form.category_id.data if form.category_id.data != -1 else None
            
            task = Task(
                title=form.title.data,
                description=form.description.data,
                user_id=current_user.id,
                category_id=category_id,
                priority=PriorityLevel[form.priority.data.upper()],
                due_date=due_date,
                recurrence=RecurrenceType[form.recurrence.data.upper()],
                is_important=form.is_important.data
            )
            
            db.session.add(task)
            db.session.flush()
            
            # Log activity
            log = ActivityLog(task_id=task.id, action='created')
            db.session.add(log)
            db.session.commit()
            
            flash(f'Task "{task.title}" created successfully!', 'success')
            return redirect(url_for('tasks'))
        
        return render_template('create_task.html', form=form)
    
    @app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(task_id):
        """Edit a task"""
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.user_id != current_user.id:
            flash('You do not have permission to edit this task.', 'danger')
            return redirect(url_for('tasks'))
        
        form = TaskForm()
        categories = Category.query.filter_by(user_id=current_user.id).all()
        form.category_id.choices = [(-1, 'No Category')] + [(c.id, c.name) for c in categories]
        
        if form.validate_on_submit():
            task.title = form.title.data
            task.description = form.description.data
            task.priority = PriorityLevel[form.priority.data.upper()]
            task.is_important = form.is_important.data
            task.recurrence = RecurrenceType[form.recurrence.data.upper()]
            
            if form.due_date.data:
                try:
                    task.due_date = datetime.fromisoformat(form.due_date.data)
                except:
                    flash('Invalid date format', 'danger')
                    return render_template('edit_task.html', form=form, task=task)
            
            category_id = form.category_id.data if form.category_id.data != -1 else None
            task.category_id = category_id
            task.updated_at = datetime.utcnow()
            
            # Log activity
            log = ActivityLog(task_id=task.id, action='edited')
            db.session.add(log)
            db.session.commit()
            
            flash(f'Task "{task.title}" updated successfully!', 'success')
            return redirect(url_for('tasks'))
        
        elif request.method == 'GET':
            form.title.data = task.title
            form.description.data = task.description
            form.priority.data = task.priority.value
            form.category_id.data = task.category_id or -1
            form.due_date.data = task.due_date.isoformat() if task.due_date else ''
            form.recurrence.data = task.recurrence.value
            form.is_important.data = task.is_important
        
        return render_template('edit_task.html', form=form, task=task)
    
    @app.route('/task/<int:task_id>/delete', methods=['POST'])
    @login_required
    def delete_task(task_id):
        """Delete a task"""
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.user_id != current_user.id:
            flash('You do not have permission to delete this task.', 'danger')
            return redirect(url_for('tasks'))
        
        task_title = task.title
        db.session.delete(task)
        db.session.commit()
        
        flash(f'Task "{task_title}" deleted successfully!', 'success')
        return redirect(url_for('tasks'))
    
    @app.route('/task/<int:task_id>/toggle', methods=['POST'])
    @login_required
    def toggle_task_completion(task_id):
        """Toggle task completion status"""
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if task.is_completed:
            task.mark_incomplete()
        else:
            task.mark_completed()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_completed': task.is_completed,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        })
    
    @app.route('/task/<int:task_id>/important', methods=['POST'])
    @login_required
    def toggle_task_important(task_id):
        """Toggle task important status"""
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        task.toggle_important()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_important': task.is_important
        })
    
    @app.route('/task/<int:task_id>')
    @login_required
    def task_detail(task_id):
        """View task details"""
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.user_id != current_user.id:
            flash('You do not have permission to view this task.', 'danger')
            return redirect(url_for('tasks'))
        
        activity_logs = ActivityLog.query.filter_by(task_id=task.id).order_by(ActivityLog.created_at.desc()).all()
        
        return render_template('task_detail.html', task=task, activity_logs=activity_logs)
    
    # ==================== Subtask Routes ====================
    
    @app.route('/task/<int:task_id>/subtask/add', methods=['POST'])
    @login_required
    def add_subtask(task_id):
        """Add a subtask"""
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        subtask = Subtask(
            title=title,
            task_id=task_id,
            order=len(task.subtasks)
        )
        db.session.add(subtask)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'subtask': {
                'id': subtask.id,
                'title': subtask.title,
                'is_completed': subtask.is_completed
            }
        })
    
    @app.route('/subtask/<int:subtask_id>/toggle', methods=['POST'])
    @login_required
    def toggle_subtask(subtask_id):
        """Toggle subtask completion"""
        subtask = Subtask.query.get_or_404(subtask_id)
        task = subtask.task
        
        # Check authorization
        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        subtask.is_completed = not subtask.is_completed
        if subtask.is_completed:
            subtask.completed_at = datetime.utcnow()
        else:
            subtask.completed_at = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_completed': subtask.is_completed
        })
    
    @app.route('/subtask/<int:subtask_id>/delete', methods=['POST'])
    @login_required
    def delete_subtask(subtask_id):
        """Delete a subtask"""
        subtask = Subtask.query.get_or_404(subtask_id)
        task = subtask.task
        
        # Check authorization
        if task.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(subtask)
        db.session.commit()
        
        return jsonify({'success': True})
    
    # ==================== Category Routes ====================
    
    @app.route('/categories')
    @login_required
    def categories():
        """View all categories"""
        categories = Category.query.filter_by(user_id=current_user.id).all()
        return render_template('categories.html', categories=categories)
    
    @app.route('/category/new', methods=['GET', 'POST'])
    @login_required
    def create_category():
        """Create a new category"""
        form = CategoryForm()
        if form.validate_on_submit():
            category = Category(
                name=form.name.data,
                description=form.description.data,
                color=form.color.data,
                user_id=current_user.id
            )
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{category.name}" created successfully!', 'success')
            return redirect(url_for('categories'))
        
        return render_template('create_category.html', form=form)
    
    @app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_category(category_id):
        """Edit a category"""
        category = Category.query.get_or_404(category_id)
        
        # Check authorization
        if category.user_id != current_user.id:
            flash('You do not have permission to edit this category.', 'danger')
            return redirect(url_for('categories'))
        
        form = CategoryForm()
        if form.validate_on_submit():
            category.name = form.name.data
            category.description = form.description.data
            category.color = form.color.data
            category.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Category "{category.name}" updated successfully!', 'success')
            return redirect(url_for('categories'))
        
        elif request.method == 'GET':
            form.name.data = category.name
            form.description.data = category.description
            form.color.data = category.color
        
        return render_template('edit_category.html', form=form, category=category)
    
    @app.route('/category/<int:category_id>/delete', methods=['POST'])
    @login_required
    def delete_category(category_id):
        """Delete a category"""
        category = Category.query.get_or_404(category_id)
        
        # Check authorization
        if category.user_id != current_user.id:
            flash('You do not have permission to delete this category.', 'danger')
            return redirect(url_for('categories'))
        
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        flash(f'Category "{category_name}" deleted successfully!', 'success')
        return redirect(url_for('categories'))
    
    @app.route('/category/<int:category_id>')
    @login_required
    def category_tasks(category_id):
        """View tasks in a category"""
        category = Category.query.get_or_404(category_id)
        
        # Check authorization
        if category.user_id != current_user.id:
            flash('You do not have permission to view this category.', 'danger')
            return redirect(url_for('categories'))
        
        page = request.args.get('page', 1, type=int)
        tasks = Task.query.filter_by(
            user_id=current_user.id,
            category_id=category_id
        ).order_by(Task.priority.desc(), Task.due_date).paginate(page=page, per_page=10)
        
        return render_template('category_tasks.html', category=category, tasks=tasks)
    
    # ==================== Tag Routes ====================
    
    @app.route('/tags')
    @login_required
    def tags():
        """View all tags"""
        tags = Tag.query.filter_by(user_id=current_user.id).all()
        return render_template('tags.html', tags=tags)
    
    @app.route('/tag/new', methods=['GET', 'POST'])
    @login_required
    def create_tag():
        """Create a new tag"""
        form = TagForm()
        if form.validate_on_submit():
            # Check if tag already exists
            existing_tag = Tag.query.filter_by(
                name=form.name.data,
                user_id=current_user.id
            ).first()
            
            if existing_tag:
                flash('This tag already exists.', 'warning')
                return redirect(url_for('tags'))
            
            tag = Tag(
                name=form.name.data,
                user_id=current_user.id
            )
            db.session.add(tag)
            db.session.commit()
            flash(f'Tag "{tag.name}" created successfully!', 'success')
            return redirect(url_for('tags'))
        
        return render_template('create_tag.html', form=form)
    
    @app.route('/tag/<int:tag_id>/delete', methods=['POST'])
    @login_required
    def delete_tag(tag_id):
        """Delete a tag"""
        tag = Tag.query.get_or_404(tag_id)
        
        # Check authorization
        if tag.user_id != current_user.id:
            flash('You do not have permission to delete this tag.', 'danger')
            return redirect(url_for('tags'))
        
        tag_name = tag.name
        db.session.delete(tag)
        db.session.commit()
        flash(f'Tag "{tag_name}" deleted successfully!', 'success')
        return redirect(url_for('tags'))
    
    @app.route('/tag/<int:tag_id>')
    @login_required
    def tag_tasks(tag_id):
        """View tasks with a specific tag"""
        tag = Tag.query.get_or_404(tag_id)
        
        # Check authorization
        if tag.user_id != current_user.id:
            flash('You do not have permission to view this tag.', 'danger')
            return redirect(url_for('tags'))
        
        page = request.args.get('page', 1, type=int)
        tasks = tag.tasks.filter_by(user_id=current_user.id).order_by(
            Task.priority.desc(), Task.due_date
        ).paginate(page=page, per_page=10)
        
        return render_template('tag_tasks.html', tag=tag, tasks=tasks)
    
    @app.route('/task/<int:task_id>/tag/<int:tag_id>/add', methods=['POST'])
    @login_required
    def add_tag_to_task(task_id, tag_id):
        """Add a tag to a task"""
        task = Task.query.get_or_404(task_id)
        tag = Tag.query.get_or_404(tag_id)
        
        # Check authorization
        if task.user_id != current_user.id or tag.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if tag not in task.tags:
            task.tags.append(tag)
            db.session.commit()
        
        return jsonify({'success': True})
    
    @app.route('/task/<int:task_id>/tag/<int:tag_id>/remove', methods=['POST'])
    @login_required
    def remove_tag_from_task(task_id, tag_id):
        """Remove a tag from a task"""
        task = Task.query.get_or_404(task_id)
        tag = Tag.query.get_or_404(tag_id)
        
        # Check authorization
        if task.user_id != current_user.id or tag.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if tag in task.tags:
            task.tags.remove(tag)
            db.session.commit()
        
        return jsonify({'success': True})
    
    # ==================== Analytics Routes ====================
    
    @app.route('/analytics')
    @login_required
    def analytics():
        """View analytics and productivity tracking"""
        # Task statistics
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, is_completed=True).count()
        overdue_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.due_date < datetime.utcnow(),
            Task.is_completed == False
        ).count()
        
        # Daily task completion for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_stats = db.session.query(
            func.date(ActivityLog.created_at).label('date'),
            func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.task_id.in_(
                db.session.query(Task.id).filter_by(user_id=current_user.id)
            ),
            ActivityLog.action == 'completed',
            ActivityLog.created_at >= thirty_days_ago
        ).group_by(func.date(ActivityLog.created_at)).all()
        
        # Priority distribution
        priority_stats = db.session.query(
            Task.priority,
            func.count(Task.id).label('count')
        ).filter(
            Task.user_id == current_user.id,
            Task.is_completed == False
        ).group_by(Task.priority).all()
        
        # Category distribution
        category_stats = db.session.query(
            Category.name,
            func.count(Task.id).label('count')
        ).join(Task).filter(
            Task.user_id == current_user.id,
            Task.is_completed == False
        ).group_by(Category.name).all()
        
        return render_template('analytics.html',
                             total_tasks=total_tasks,
                             completed_tasks=completed_tasks,
                             overdue_tasks=overdue_tasks,
                             progress=int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0),
                             daily_stats=daily_stats,
                             priority_stats=priority_stats,
                             category_stats=category_stats)
    
    # ==================== Settings Routes ====================
    
    @app.route('/settings')
    @login_required
    def settings():
        """User settings"""
        form = UserPreferencesForm()
        if request.method == 'GET':
            form.theme.data = current_user.theme
            form.timezone.data = current_user.timezone
        
        return render_template('settings.html', form=form)
    
    @app.route('/settings/update', methods=['POST'])
    @login_required
    def update_settings():
        """Update user settings"""
        form = UserPreferencesForm()
        if form.validate_on_submit():
            current_user.theme = form.theme.data
            current_user.timezone = form.timezone.data
            db.session.commit()
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('settings'))
        
        return render_template('settings.html', form=form)
    
    # ==================== API Routes ====================
    
    @app.route('/api/tasks/stats')
    @login_required
    def api_task_stats():
        """Get task statistics as JSON"""
        stats = current_user.get_task_stats()
        return jsonify(stats)
    
    @app.route('/api/tasks/export')
    @login_required
    def api_export_tasks():
        """Export tasks as JSON"""
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return jsonify([task.to_dict() for task in tasks])
    
    # ==================== Error Handlers ====================
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return render_template('500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
