# Kanban Task Management App — Quantiphi Vibe

A modern, responsive, full-stack task management and team productivity application built with **Django**, **HTMX**, **SQLite**, **Tailwind CSS**, and **SortableJS**.

![Kanban Board](https://raw.githubusercontent.com/loowtide/quantiphi-vibe/main/static/preview.png)

---

## 🚀 Features

### 📋 Interactive Kanban Board
- **Three Core Columns**: *To-Do*, *In Progress*, and *Done* with real-time task counters.
- **Fluid Drag & Drop**: Powered by **SortableJS** and updated via asynchronous JSON/HTMX endpoints with auto position and status persistence.
- **Priority Filtering**: Quick toggle between High (🔴), Medium (🟡), and Low (🟢) priority tasks without page reloads.
- **Overdue Detection**: Automated visual indicators for overdue deadlines on active tasks.

### 👥 Team & Project Management
- **User Authentication**: Secure registration, login, logout, and user profile management (avatar, bio, initials avatar fallback).
- **Projects & Members**: Create multiple projects, invite team members, assign roles (*Owner*, *Admin*, *Member*), and manage project settings.
- **Team Workload Sidebar**: Real-time counter of active tasks per team member with an animated pulsing warning when a member is overloaded (6+ active tasks).

### 🔔 Notifications & Deadline Pings
- **Deadline Ping**: Team members can ping assignees about upcoming deadlines directly from task details.
- **Spam Cooldown**: Built-in 1-hour cooldown mechanism to prevent notification fatigue.
- **Notification Dropdown**: Instant dropdown and dedicated notification hub with read/unread statuses and mark-all-read capabilities.

### 💬 Board Discussions & Comments
- **Discussion Thread**: In-app comments section on each Kanban board powered by HTMX for instant posting and deletion without page refresh.

### 🧪 Automated Testing
- Built with **Django's built-in testing framework**.
- **23 comprehensive unit and integration tests** covering accounts, projects, tasks, comments, workload calculation, permissions, and notifications.

---

## 🛠️ Technology Stack

- **Backend**: Django 5.x
- **Frontend**: Django Templates + HTMX (`django-htmx` + `htmx.org`)
- **Drag & Drop**: SortableJS
- **Styling**: Tailwind CSS (Tailwind Play CDN with custom dark UI theme)
- **Database**: SQLite
- **Testing**: `django.test.TestCase`

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/loowtide/quantiphi-vibe.git
cd quantiphi-vibe
```

### 2. Activate virtual environment
```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Run automated tests
```bash
python manage.py test
```

### 6. Start the development server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 📁 Project Structure

```
├── accounts/          # User authentication, registration, profile
├── projects/          # Project creation, settings, member management
├── tasks/             # Kanban board, task CRUD, drag-and-drop, workload
├── comments/          # Board discussion threads and comments
├── notifications/     # Deadline reminders, notifications center, cooldowns
├── config/            # Django project settings and root URLs
├── templates/         # Clean modular HTML templates and HTMX partials
├── static/            # Custom CSS animations and Sortable styles
└── manage.py          # Django CLI management entry point
```
