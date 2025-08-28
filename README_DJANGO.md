# Smart E-Challan System - Django Version

A comprehensive Django-based Smart Electronic Challan System that automates traffic violation detection and challan generation using computer vision and AI technologies.

## 🚀 Features

### Core Functionality
- **Vehicle Management**: Complete vehicle registration and owner information management
- **Challan Generation**: Automated and manual challan creation with violation tracking
- **Object Detection**: AI-powered traffic violation detection using TensorFlow
- **Payment Tracking**: Multiple payment methods and transaction history
- **Reporting**: Comprehensive analytics and reporting dashboard
- **User Management**: Role-based access control for police officers

### Technical Features
- **Real-time Processing**: Live video stream processing with object detection
- **ROI Management**: Region of Interest selection for focused monitoring
- **Multi-database Support**: SQLite for Django, MySQL for challan data
- **RESTful APIs**: JSON endpoints for integration with mobile apps
- **Responsive UI**: Modern Bootstrap-based interface
- **File Upload**: Support for video and image evidence

## 🛠️ Technology Stack

- **Backend**: Django 5.2.3
- **Database**: SQLite (Django), MySQL (Challan data)
- **AI/ML**: TensorFlow, OpenCV, SSD MobileNet
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Python**: 3.12+
- **Additional**: PyMySQL, NumPy, Matplotlib

## 📋 Prerequisites

- Python 3.12 or higher
- MySQL Server (for challan database)
- Git
- pip/conda

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Smart-e-challan-system-master
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE id5162425_echallan;
CREATE USER 'id5162425_riya'@'localhost' IDENTIFIED BY 'Yes';
GRANT ALL PRIVILEGES ON id5162425_echallan.* TO 'id5162425_riya'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Django Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser and initial data
python manage.py setup_initial_data

# Collect static files
python manage.py collectstatic
```

### 6. Run the Application
```bash
python manage.py runserver
```

## 🔐 Default Login

- **Username**: admin
- **Password**: admin123
- **URL**: http://localhost:8000/admin/

## 📁 Project Structure

```
smart_challan_system/
├── smart_challan_system/          # Main project settings
├── challan_app/                   # Challan management app
│   ├── models.py                  # Database models
│   ├── views.py                   # Business logic
│   ├── forms.py                   # Form handling
│   ├── admin.py                   # Admin interface
│   └── management/                # Custom commands
├── object_detection/              # Object detection app
│   ├── models.py                  # Detection models
│   ├── views.py                   # Detection views
│   ├── forms.py                   # Detection forms
│   ├── admin.py                   # Detection admin
│   └── utils/                     # Detection utilities
├── templates/                     # HTML templates
├── static/                        # Static files
├── media/                         # Uploaded files
├── models/                        # TensorFlow models
└── data/                          # Label files
```

## 🎯 Usage

### 1. Access the System
- Navigate to http://localhost:8000/
- Login with admin credentials
- Access the dashboard

### 2. Vehicle Management
- Add new vehicles with owner information
- Search and filter vehicles
- View vehicle challan history

### 3. Challan Generation
- Create new challans for violations
- Upload evidence (images/videos)
- Track payment status
- Generate reports

### 4. Object Detection
- Upload video files for processing
- Configure ROIs (Regions of Interest)
- Start detection sessions
- View detection results

### 5. Reporting
- View monthly statistics
- Track revenue and violations
- Generate custom reports

## 🔧 Configuration

### Database Configuration
Edit `smart_challan_system/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'challan_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Object Detection Model
- Download SSD MobileNet model from TensorFlow
- Place in `models/` directory
- Update model paths in settings

## 📱 API Endpoints

### Challan App
- `GET /challan/api/vehicle-search/` - Search vehicles
- `POST /challan/challans/<id>/status/` - Update challan status

### Object Detection
- `GET /detection/api/sessions/<id>/results/` - Get detection results
- `POST /detection/api/start-detection/` - Start detection
- `POST /detection/api/sessions/<id>/stop/` - Stop detection

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MySQL is running
   - Check database credentials
   - Ensure database exists

2. **Model Loading Error**
   - Download required TensorFlow models
   - Check model file paths
   - Verify model compatibility

3. **Migration Errors**
   - Delete migration files and recreate
   - Check model field compatibility
   - Verify database schema

### Debug Mode
Set `DEBUG = True` in settings.py for detailed error messages.

## 🔒 Security Features

- **Authentication**: Django's built-in user authentication
- **Authorization**: Role-based access control
- **CSRF Protection**: Cross-site request forgery protection
- **SQL Injection**: ORM-based query protection
- **File Upload**: Secure file handling and validation

## 📊 Performance Optimization

- **Database Indexing**: Optimized database queries
- **Caching**: Redis/Memcached support (configurable)
- **Static Files**: CDN-ready static file serving
- **Image Processing**: Efficient image/video processing
- **Background Tasks**: Async processing for heavy operations

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False`
2. Configure production database
3. Set up static file serving
4. Configure HTTPS
5. Set up monitoring and logging

### Docker Support
```bash
# Build and run with Docker
docker build -t smart-challan .
docker run -p 8000:8000 smart-challan
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Updates

- **v1.0.0**: Initial Django release
- **v1.1.0**: Added object detection features
- **v1.2.0**: Enhanced reporting and analytics

---

**Note**: This is a Django conversion of the original Smart E-Challan System. All original functionality has been preserved and enhanced with modern web technologies.
