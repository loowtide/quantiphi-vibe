# Quantiphi Vibe

A Django + HTMX full-stack web project.

## Setup

### Prerequisites
- Python 3.13+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/loowtide/quantiphi-vibe.git
   cd quantiphi-vibe
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## Tech Stack
- **Backend**: Django
- **Frontend**: HTMX
- **Database**: SQLite (development)
