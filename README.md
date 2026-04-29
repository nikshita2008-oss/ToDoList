# To-Do List Web Application

A comprehensive task management web application built with Python Flask. Organize your tasks with categories, tags, priorities, and due dates. Track productivity with analytics and enjoy a responsive design with dark/light mode support.

## Features

### Core Task Management
- ✅ Create, read, update, and delete tasks
- 📝 Add task titles, descriptions, and notes
- 📅 Set due dates and times
- 🎯 Assign priority levels (High, Medium, Low)
- ⭐ Mark tasks as important
- ✔️ Track task completion status
- 📊 View completion percentage

### Task Organization
- 📂 Create multiple categories (Work, Personal, Shopping, etc.)
- 🏷️ Tag tasks with multiple labels
- 📌 Break tasks into subtasks
- 🔄 Filter tasks by various criteria
- 🔍 Search tasks by keywords

### Time Management
- 📆 Set and track due dates
- ⏰ Get overdue task alerts
- 🔄 Support for recurring tasks (Daily, Weekly, Monthly)
- 📊 Track completion history

### Advanced Features
- 👤 User authentication (Signup/Login)
- 📈 Analytics and productivity tracking
- 🌓 Dark/Light theme support
- 📱 Fully responsive design
- 💾 Data persistence
- 📤 Export tasks as JSON

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Setup the Project
```bash
cd "To Do List"
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize the Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

Or run the provided script:
```bash
python init_db.py
```

## Running the Application

### Start the Development Server
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Using the Run Script (Windows)
```bash
./run.bat
```

### Using the Run Script (macOS/Linux)
```bash
./run.sh
```

## Default Credentials

After initialization, you'll need to create an account:
1. Go to http://localhost:5000/register
2. Create a new account
3. Log in with your credentials

## Project Structure

```
To-Do List/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── forms.py               # WTForms form definitions
├── requirements.txt       # Python dependencies
├── todolist.db            # SQLite database (created on first run)
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Dashboard
│   ├── tasks.html        # Tasks list
│   ├── task_detail.html  # Task detail page
│   ├── create_task.html  # Create task form
│   ├── edit_task.html    # Edit task form
│   ├── categories.html   # Categories list
│   ├── tags.html         # Tags list
│   ├── analytics.html    # Analytics page
│   ├── settings.html     # User settings
│   ├── 404.html         # 404 error page
│   └── 500.html         # 500 error page
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   └── js/
│       └── app.js       # JavaScript functionality
└── README.md            # This file
```

## Database Models

### User
- User authentication and profile management
- Theme preferences (light/dark)
- Timezone settings

### Task
- Core task entity with title, description, priority
- Due dates and recurrence patterns
- Completion tracking and timestamps

### Category
- Organize tasks into categories
- Custom colors for visual organization
- Task grouping

### Tag
- Label tasks with multiple tags
- Many-to-many relationship with tasks

### Subtask
- Break down complex tasks
- Track completion independently

### ActivityLog
- Track task history
- Record creation, editing, and completion events

## Usage Guide

### Creating a Task
1. Click "+ New Task" button
2. Fill in task details:
   - Title (required)
   - Description (optional)
   - Category (optional)
   - Priority level
   - Due date and time
   - Recurrence pattern
3. Click "Create Task"

### Managing Tasks
- **Mark Complete**: Click the checkbox next to a task
- **Edit**: Click the edit icon or task title
- **Delete**: Click the delete icon with confirmation
- **Star/Important**: Click the star icon to mark as important
- **Add Subtasks**: Open task details and add subtasks

### Organizing Tasks
- Create categories for different areas (Work, Personal, etc.)
- Add tags to tasks for flexible labeling
- Use categories and tags to filter tasks
- Search by keyword in the search bar

### Viewing Analytics
- Go to "Analytics" page to see:
  - Overall progress and statistics
  - Tasks by priority distribution
  - Tasks by category distribution
  - Completion trends
  - Personalized insights

### Settings
- Toggle between light and dark themes
- Set your timezone
- Export all tasks as JSON
- Manage your account

## Keyboard Shortcuts

- **Ctrl/Cmd + N**: Create new task
- **Ctrl/Cmd + F**: Focus search bar
- **Escape**: Close modals or cancel forms

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Tasks
- `GET /tasks` - View all tasks with filters
- `POST /task/new` - Create new task
- `GET /task/<id>` - View task details
- `POST /task/<id>/edit` - Edit task
- `POST /task/<id>/delete` - Delete task
- `POST /task/<id>/toggle` - Toggle task completion
- `POST /task/<id>/important` - Toggle important status

### Subtasks
- `POST /task/<id>/subtask/add` - Add subtask
- `POST /subtask/<id>/toggle` - Toggle subtask completion
- `POST /subtask/<id>/delete` - Delete subtask

### Categories
- `GET /categories` - View all categories
- `POST /category/new` - Create category
- `POST /category/<id>/edit` - Edit category
- `POST /category/<id>/delete` - Delete category
- `GET /category/<id>` - View category tasks

### Tags
- `GET /tags` - View all tags
- `POST /tag/new` - Create tag
- `POST /tag/<id>/delete` - Delete tag
- `GET /tag/<id>` - View tag tasks

### Analytics
- `GET /analytics` - View analytics
- `GET /api/tasks/stats` - Get task statistics (JSON)
- `GET /api/tasks/export` - Export all tasks (JSON)

## Customization

### Change Database
Edit `config.py` to use a different database:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/todolist'
```

### Modify Styling
Edit `static/css/style.css` to customize colors, fonts, and layout.

### Add Features
Extend the application by:
1. Adding new models in `models.py`
2. Creating new routes in `app.py`
3. Adding new templates in `templates/`
4. Adding JavaScript functions in `static/js/app.js`

## Troubleshooting

### Database Issues
```bash
# Delete the database and reinitialize
rm todolist.db
python init_db.py
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Module Not Found
Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

## Future Enhancements

- 📧 Email notifications and reminders
- 🔄 Task synchronization across devices
- ☁️ Cloud storage integration
- 📊 Advanced analytics and reports
- 🤖 AI-powered task suggestions
- 🔔 Browser push notifications
- 📱 Mobile app
- 👥 Collaboration and sharing
- 🧠 Smart task prioritization
- 📈 Time tracking

## Technologies Used

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database
- **Flask-Login**: User authentication
- **Flask-WTF**: Form handling

### Frontend
- **HTML5**: Markup
- **CSS3**: Styling with variables and animations
- **JavaScript**: Interactivity and DOM manipulation
- **Responsive Design**: Mobile-first approach

### Database
- **SQLite**: Default database (can be replaced)

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- User authentication and authorization
- Session management
- Input validation and sanitization

## Performance Considerations

- Database indexing on frequently queried fields
- Pagination for task lists
- Query optimization with lazy loading
- CSS and JS minification ready
- Responsive images and assets

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information

## Changelog

### Version 1.0.0
- Initial release
- Core task management
- Categories and tags
- User authentication
- Analytics and productivity tracking
- Dark/light mode
- Responsive design

---

**Enjoy organizing your tasks!** 🎯

For more information or updates, visit the project repository.
