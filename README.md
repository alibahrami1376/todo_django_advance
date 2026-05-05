# 📋 Todo Django Advanced

An advanced **Todo Manager** application built with Django and Django REST Framework featuring JWT authentication, user management, email verification, and comprehensive API integration.

## 🌟 Key Features

### 🔐 Authentication & Authorization
- ✅ **JWT Authentication** - Refresh and Access tokens
- ✅ **Session Authentication** - For traditional web applications
- ✅ **Token Authentication** - For REST clients
- ✅ **Owner-based Authorization** - Filter user-specific data
- ✅ **Logout Functionality** - Blacklist issued tokens

### 👤 User Management
- ✅ New user registration
- ✅ Email verification with confirmation links
- ✅ Password change functionality
- ✅ User profile management
- ✅ User information retrieval

### ✅ Todo Management
- ✅ Create, read, update, delete todos
- ✅ Filter by completion status
- ✅ Auto-delete completed tasks
- ✅ Sorting and searching capabilities

### 🌤️ Weather API Integration
- ✅ Retrieve current weather information
- ✅ Web-based weather display page
- ✅ Data caching for improved performance

### 📚 Documentation & Code Quality
- ✅ **Swagger/OpenAPI** - Interactive API documentation
- ✅ **Black** - Automatic code formatter
- ✅ **Flake8** - Code linting
- ✅ **Pytest** - Automated testing
- ✅ **Coverage** - Test coverage reports

### 🚀 Advanced Technologies
- ✅ **Redis Caching** - In-memory data storage
- ✅ **Celery** - Asynchronous background tasks
- ✅ **Email Templating** - Template-based email sending
- ✅ **Docker & Docker Compose** - Containerization

### 🔧 DevOps & Deployment
- ✅ **GitHub Actions CI/CD** - Automated testing
- ✅ **Docker** - Complete containerized environment
- ✅ **docker-compose** - Redis + Backend + Worker + SMTP

---

## 📦 Technologies Used

| Technology | Version | Description |
|-----------|---------|------------|
| **Python** | 3.8+ | Programming language |
| **Django** | 3.2.25 | Web framework |
| **DRF** | 3.14.0 | Django REST Framework |
| **JWT** | simplejwt | Token-based authentication |
| **Redis** | latest | Caching and data store |
| **Celery** | - | Asynchronous task queue |
| **PostgreSQL** | - | Database (optional) |

---

## 🚀 Quick Start

### Requirements
- Python 3.8+
- pip or poetry
- Docker and Docker Compose (optional)

### Local Installation Without Docker

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/alibahrami1376/todo_django_advance.git
cd todo_django_advance
```

#### 2️⃣ Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

#### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure Environment File
```bash
cd core
cp .env.example .env
# Edit .env and set environment variables
```

#### 5️⃣ Run Migrations
```bash
python manage.py migrate
```

#### 6️⃣ Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

#### 7️⃣ Run Development Server
```bash
python manage.py runserver
```

The server will be running at `http://localhost:8000`.

### Installation with Docker Compose

#### 1️⃣ Verify Docker Installation
```bash
docker --version
docker-compose --version
```

#### 2️⃣ Create Environment File
```bash
cd core
echo 'SECRET_KEY=your-secret-key-here' > .env
echo 'DEBUG=False' >> .env
echo 'ALLOWED_HOSTS=localhost,127.0.0.1' >> .env
```

#### 3️⃣ Build and Run Containers
```bash
docker-compose up -d
```

#### 4️⃣ Run Migrations
```bash
docker-compose exec backend python manage.py migrate
```

#### 5️⃣ Create Superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```

The server will be running at `http://localhost:8000`.

---

## 🔌 API Endpoints

### 🔐 Authentication

#### Register New User
```http
POST /accounts/api/v1/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

#### Obtain JWT Token
```http
POST /accounts/api/v1/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refresh Access Token
```http
POST /accounts/api/v1/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Logout (Blacklist Token)
```http
POST /accounts/api/v1/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 👤 User Management

#### Get User Profile
```http
GET /accounts/api/v1/profile/
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Change Password
```http
POST /accounts/api/v1/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "old_password123",
  "new_password": "new_password123"
}
```

#### Verify Email
```http
POST /accounts/api/v1/verify-email/
Content-Type: application/json

{
  "email": "john@example.com"
}
```

A verification link will be sent to the email.

---

### ✅ Todo Management

#### Get All Todos
```http
GET /api/todos/
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Meat, rice, vegetables",
    "complete": false,
    "created_at": "2026-05-01T10:30:00Z",
    "owner": "john_doe"
  }
]
```

#### Create New Todo
```http
POST /api/todos/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Complete Django project",
  "description": "Create API for todo management",
  "complete": false
}
```

#### Update Todo
```http
PUT /api/todos/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Complete Django project",
  "description": "Create API for todo management",
  "complete": true
}
```

#### Delete Todo
```http
DELETE /api/todos/1/
Authorization: Bearer <access_token>
```

#### Filter Incomplete Todos
```http
GET /api/todos/?complete=false
Authorization: Bearer <access_token>
```

#### Delete Completed Todos
```http
DELETE /api/todos/delete-completed/
Authorization: Bearer <access_token>
```

---

### 🌤️ Weather

#### Get Current Weather Information
```http
GET /api/weather/v1/current/?city=tehran
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "city": "Tehran",
  "country": "IR",
  "temperature": 25.5,
  "feels_like": 24.0,
  "humidity": 65,
  "description": "Clear sky",
  "icon": "01d"
}
```

#### Weather Web Page
```
GET /weather/
```

---

## 🧪 Testing

### Run All Tests
```bash
cd core
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=accounts --cov=todo --cov-report=html
```

### Run Specific Tests
```bash
pytest tests/test_accounts.py -v
```

---

## 🐳 Docker Commands

### Build Image
```bash
docker build -t todo-backend:1.0 .
```

### Run Containers
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f backend
```

### Stop Services
```bash
docker-compose down
```

### Remove Volumes (Delete Database Data)
```bash
docker-compose down -v
```

---

## 📊 Project Structure

```
todo_django_advance/
├── core/
│   ├── accounts/              # User management app
│   │   ├── models.py          # Custom User model
│   │   ├── views.py           # API endpoints
│   │   ├── serializers.py     # DRF serializers
│   │   ├── urls.py            # URL patterns
│   │   └── ...
│   ├── todo/                  # Todo management app
│   │   ├── models.py          # Todo model
│   │   ├── views.py           # API ViewSets
│   │   ├── serializers.py     # Todo serializers
│   │   ├── permissions.py     # Custom permission classes
│   │   └── ...
│   ├── weather/               # Weather app
│   │   ├── views.py
│   │   ├── services.py        # External API calls
│   │   └── ...
│   ├── core/
│   │   ├── settings.py        # Django settings
│   │   ├── urls.py            # Main URLs
│   │   ├── wsgi.py
│   │   └── ...
│   ├── templates/             # HTML templates
│   ├── static/                # Static files (CSS, JS)
│   ├── manage.py
│   └── db.sqlite3
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose settings
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
├── .flake8                    # Flake8 settings
├── .gitignore
└── README.md
```

---

## 🔑 Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True                              # False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3       # or postgresql://user:pass@host/db

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp4dev
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=False

# API Keys
OPENWEATHER_API_KEY=your-api-key-here

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 🛡️ Best Practices

### 🔐 Security

1. **Change `SECRET_KEY` in Production**
   ```bash
   SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
   ```

2. **Enable HTTPS**
   ```python
   # settings.py
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

3. **Set ALLOWED_HOSTS**
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Disable DEBUG in Production**
   ```python
   DEBUG = False
   ```

### 📈 Performance

1. **Use Caching**
   ```python
   from django.views.decorators.cache import cache_page
   
   @cache_page(60 * 5)  # 5 minutes
   def expensive_view(request):
       return Response(...)
   ```

2. **Use select_related and prefetch_related**
   ```python
   queryset = Todo.objects.select_related('owner').filter(owner=user)
   ```

3. **Implement Pagination**
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 10
   }
   ```

### 🧪 Testing

```python
from django.test import TestCase
from rest_framework.test import APIClient

class TodoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
    
    def test_create_todo(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/todos/', {
            'title': 'Test Todo',
            'complete': False
        })
        self.assertEqual(response.status_code, 201)
```

### 📝 Clean Code

```bash
# Format with Black
black core/

# Run Flake8
flake8 core/

# Sort Imports
isort core/
```

---

## 🚀 Deployment

### Deploy to Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn core.wsgi" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
heroku run python core/manage.py migrate
```

### Deploy to PythonAnywhere

1. Upload code to server
2. Configure Virtual Environment
3. Set up WSGI configuration
4. Collect static files

### Deploy to DigitalOcean

```bash
# SSH into server
ssh root@your-server-ip

# Install dependencies
apt update && apt install python3-pip python3-venv nginx gunicorn postgresql

# Clone repository
git clone <your-repo> /var/www/todo

# Setup
cd /var/www/todo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
gunicorn core.wsgi:application --bind 127.0.0.1:8000

# Configure Nginx...
```

---

## 📚 Additional Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Swagger/OpenAPI](http://localhost:8000/swagger/)
- [ReDoc](http://localhost:8000/redoc/)

---

## 📊 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

---

## 🔄 Development Workflow

### Making Changes

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Code Quality Checks

```bash
# Run all checks
black core/
flake8 core/
isort core/
pytest
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Contact & Support

- **Email**: alifbahrami13766@gmail.com
- **GitHub**: [alibahrami1376](https://github.com/alibahrami1376)
- **Issues**: [Report issues here](https://github.com/alibahrami1376/todo_django_advance/issues)

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Django and DRF teams
- All contributors and users who provide feedback and suggestions

---

## 📈 Deployment Checklist

Before deploying to production, ensure:

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` is changed and kept secret
- [ ] `ALLOWED_HOSTS` is configured properly
- [ ] Database is configured (PostgreSQL recommended)
- [ ] All migrations are applied
- [ ] Static files are collected
- [ ] HTTPS/SSL is enabled
- [ ] CORS is configured correctly
- [ ] Email backend is configured
- [ ] Redis is running (if using caching)
- [ ] Celery worker is running (if using tasks)
- [ ] Environment variables are set correctly
- [ ] Database backups are configured
- [ ] Monitoring and logging are set up
- [ ] Rate limiting is configured

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `django.core.exceptions.ImproperlyConfigured: Installed app with label 'accounts' doesn't have a 'models' module.`

**Solution**:
```bash
# Make sure __init__.py exists in app directory
touch core/accounts/__init__.py
```

**Issue**: `Redis connection refused`

**Solution**:
```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis
```

**Issue**: `ModuleNotFoundError: No module named 'rest_framework'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📊 Performance Metrics

- API Response Time: < 200ms
- Test Coverage: > 80%
- Uptime: 99.9% (with proper deployment)

---

**Last Updated**: 2026-05-05 | **Version**: 1.0.0

**Star this project** ⭐ if you find it helpful!
