# Contact Book Django Project

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

## Setup Instructions

### 1. Clone repository

```bash
git clone <repo-url>
cd contact-book-django
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Start Docker services

```bash
docker compose up -d
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

### 8. Run development server

```bash
python manage.py runserver
```

## Access Points

- Django Admin: http://localhost:8000/admin
- PgAdmin: http://localhost:5050
- API: http://localhost:8000/api

## Docker Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f postgres

# Database shell
docker exec -it contact_book_postgres psql -U contact_user -d contact_book_db
```

## Project Structure

```
contact-book-django/
├── docker/                    # Docker configuration
├── contact_book_project/     # Django settings
├── contacts/                 # Contacts app
├── docker-compose.yml        # Docker Compose config
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```
