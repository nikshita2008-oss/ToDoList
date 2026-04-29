# Quick Start Guide - To-Do List Application

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd "To Do List"
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python init_db.py
```

### Step 3: Start the Server
**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
bash run.sh
```

### Step 4: Access the Application
Open your browser and go to:
```
http://localhost:5000
```

### Step 5: Create an Account or Login with Demo
- **Register**: Create a new account
- **Demo Account** (if created during init):
  - Email: demo@example.com
  - Password: demo123

## 📋 What You Can Do

1. **Create Tasks** - Click "+ New Task" to add items to your to-do list
2. **Organize** - Use categories and tags to organize your tasks
3. **Prioritize** - Set priority levels (High/Medium/Low) and mark important tasks
4. **Track Progress** - Check the dashboard for your productivity stats
5. **Customize** - Switch between light and dark themes in settings

## 🎯 Key Features

| Feature | How to Use |
|---------|-----------|
| Create Task | Click "+ New Task" button |
| Edit Task | Click on a task and select "Edit" |
| Complete Task | Check the checkbox next to a task |
| Search | Use the search bar in the Tasks page |
| Filter | Use the filter options to narrow down tasks |
| View Analytics | Click "Analytics" in navigation |
| Settings | Click "Settings" to customize preferences |

## 🌓 Dark Mode

Click the theme toggle button (☀️/🌙) in the top right corner to switch themes.

## 📁 Project Files Overview

```
To Do List/
├── app.py                  - Main application (run this to start)
├── models.py               - Database models
├── forms.py                - Form definitions
├── config.py               - Configuration
├── init_db.py              - Database initialization script
├── run.bat / run.sh        - Quick start scripts
├── requirements.txt        - Dependencies
├── README.md               - Full documentation
├── templates/              - HTML pages
└── static/                 - CSS & JavaScript
```

## 🛠️ Troubleshooting

**Issue**: Port 5000 is already in use
- Solution: Edit `app.py` and change the port number

**Issue**: Database error
- Solution: Delete `todolist.db` and run `python init_db.py` again

**Issue**: Dependencies not installed
- Solution: Run `pip install -r requirements.txt`

## 📚 Learn More

- Full documentation: See [README.md](README.md)
- API endpoints: See [README.md](README.md#api-endpoints)
- Customization guide: See [README.md](README.md#customization)

## 💡 Tips

1. Use keyboard shortcuts:
   - `Ctrl+N` to create a new task
   - `Ctrl+F` to focus the search bar
   - `Escape` to close modals

2. Create categories for different life areas (Work, Personal, Shopping, etc.)

3. Use tags like "Urgent", "Important", "Later" for flexible organization

4. Check the Dashboard to see your daily tasks and progress

5. Use the Analytics page to track productivity trends

## 🚀 Next Steps

1. Create your first task
2. Add a category
3. Mark the task as complete
4. Check your progress in the Dashboard
5. Explore the Analytics page

---

**Happy organizing!** 🎯

For detailed information, check the [README.md](README.md) file.
