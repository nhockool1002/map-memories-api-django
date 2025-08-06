# Map Memories API - Django Implementation

A Django-based RESTful API for managing location-based memories with media attachments, virtual currency system, and shop functionality.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### 1. Clone and Start

```bash
git clone <repository-url>
cd map-memories-django
docker-compose up -d
```

### 2. Access the Application

- **API Base URL**: http://localhost:8090/api/v1/
- **Admin Panel**: http://localhost:8090/admin/
- **API Documentation**: http://localhost:8090/api/docs/
- **Health Check**: http://localhost:8090/health/

### 3. Default Admin Account

- **Email**: `admin@admin.com`
- **Password**: `admin`

## 📋 Project Structure

```
map-memories-django/
├── map_memories/           # Django project settings
├── accounts/              # User authentication and management
├── locations/             # Location management with PostGIS
├── memories/              # Memory management (1-1 with locations)
├── media/                 # File upload and media handling
├── shop/                  # Virtual shop and currency system
├── common/                # Shared utilities and base models
├── docker-compose.yml     # Docker services configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🐳 Docker Configuration

### Services

- **mmdj_db**: PostgreSQL 15 with PostGIS (Port: 5433)
- **mmdj_redis**: Redis 7 for caching (Port: 6380)
- **mmdj_api**: Django application (Port: 8090)
- **mmdj_nginx**: Nginx reverse proxy (Port: 80)

### Custom Ports (as requested)

- PostgreSQL: `5433` (instead of default 5432)
- Django App: `8090` (instead of default 8000/8080)
- Redis: `6380` (instead of default 6379)
- Nginx: `80`

## 🔧 Development Setup

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f mmdj_api

# Run Django commands
docker-compose exec mmdj_api python manage.py shell
docker-compose exec mmdj_api python manage.py migrate
docker-compose exec mmdj_api python manage.py seed_data

# Stop services
docker-compose down
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5433
export DB_NAME=map_memories_db
export DB_USER=mmdj_user
export DB_PASSWORD=mmdj_password123

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed sample data
python manage.py seed_data

# Run development server
python manage.py runserver 8090
```

## 🗄️ Database

### PostgreSQL with PostGIS

The application uses PostgreSQL 15 with PostGIS extension for geospatial functionality.

### Database Tables (with mm_ prefix)

- `mm_users` - User accounts with soft delete
- `mm_locations` - Geographic locations
- `mm_memories` - User memories (1-1 with locations)
- `mm_media` - Media files (Base64 storage)
- `mm_shop_items` - Shop items for purchase
- `mm_user_items` - User-owned items
- `mm_transaction_logs` - Currency transaction history
- `mm_user_sessions` - JWT session management
- `mm_memory_likes` - Memory likes/favorites

### Soft Delete Implementation

All main entities support soft delete:
- Records are marked with `deleted_at` timestamp instead of hard deletion
- Default manager excludes soft-deleted records
- `all_objects` manager includes soft-deleted records
- Related records are automatically soft-deleted

### Memory-Location Relationship (as requested)

- **One-to-One relationship**: Each memory can have exactly one location
- **Cascading delete**: When memory is deleted, associated location is also deleted
- This differs from the original API design but follows your requirements

## 🔐 Authentication

### JWT Authentication

- **Access Token**: 24 hours lifetime
- **Refresh Token**: 7 days lifetime
- **Headers**: `Authorization: Bearer <token>`

### User Types

1. **Regular Users**: Can create memories, locations, purchase items
2. **Admin Users**: Full access including user management and shop administration

## 📡 API Endpoints

### Authentication Endpoints

```http
POST /api/v1/auth/register/     # User registration
POST /api/v1/auth/login/        # User login
GET  /api/v1/auth/profile/      # Get user profile
PUT  /api/v1/auth/profile/      # Update user profile
POST /api/v1/auth/logout/       # Logout (invalidate token)
```

### Location Endpoints

```http
GET    /api/v1/locations/           # List locations
POST   /api/v1/locations/           # Create location
GET    /api/v1/locations/{uuid}/    # Get location details
PUT    /api/v1/locations/{uuid}/    # Update location
DELETE /api/v1/locations/{uuid}/    # Delete location
GET    /api/v1/locations/nearby/    # Search nearby locations
```

### Memory Endpoints

```http
GET    /api/v1/memories/           # List memories
POST   /api/v1/memories/           # Create memory
GET    /api/v1/memories/{uuid}/    # Get memory details
PUT    /api/v1/memories/{uuid}/    # Update memory
DELETE /api/v1/memories/{uuid}/    # Delete memory
POST   /api/v1/memories/{uuid}/like/   # Toggle like
```

### Media Endpoints

```http
POST   /api/v1/media/upload/       # Upload media file
GET    /api/v1/media/               # List user's media
GET    /api/v1/media/{uuid}/        # Get media details
PUT    /api/v1/media/{uuid}/        # Update media
DELETE /api/v1/media/{uuid}/        # Delete media
GET    /api/v1/media/{uuid}/file/   # Serve media file
```

### Shop Endpoints

```http
GET    /api/v1/shop/items/          # Browse shop items
GET    /api/v1/shop/items/{uuid}/   # Get shop item details
POST   /api/v1/shop/purchase/       # Purchase item
GET    /api/v1/shop/my-items/       # Get user's items
```

### Currency Endpoints

```http
GET    /api/v1/currency/balance/    # Get user balance
GET    /api/v1/currency/history/    # Get transaction history
```

### Admin Endpoints

```http
POST   /api/v1/admin/shop/items/              # Create shop item
PUT    /api/v1/admin/shop/items/{uuid}/       # Update shop item
DELETE /api/v1/admin/shop/items/{uuid}/       # Delete shop item
POST   /api/v1/admin/currency/add/            # Add currency to user
POST   /api/v1/admin/currency/subtract/       # Subtract currency from user
GET    /api/v1/admin/currency/history/        # View user transactions
```

## 📊 API Response Format

### Success Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data
  },
  "pagination": {  // For paginated responses
    "current_page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error description",
  "error_type": "validation_error",
  "status_code": 400,
  "errors": {
    "field_name": ["Error message"]
  }
}
```

## 🔍 Sample API Usage

### 1. User Registration

```bash
curl -X POST http://localhost:8090/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. User Login

```bash
curl -X POST http://localhost:8090/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Create Memory with Location

```bash
# First create location
curl -X POST http://localhost:8090/api/v1/locations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Beautiful Coffee Shop",
    "description": "My favorite coffee place",
    "latitude": 21.0285,
    "longitude": 105.8542,
    "address": "Hanoi, Vietnam",
    "city": "Hanoi",
    "country": "Vietnam"
  }'

# Then create memory linked to location
curl -X POST http://localhost:8090/api/v1/memories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "LOCATION_UUID",
    "title": "Amazing Coffee Experience",
    "content": "Had the best latte here today!",
    "visit_date": "2024-01-15",
    "is_public": true,
    "tags": ["coffee", "hanoi", "favorite"]
  }'
```

### 4. Search Nearby Locations

```bash
curl "http://localhost:8090/api/v1/locations/nearby/?latitude=21.0285&longitude=105.8542&radius=5&limit=10"
```

### 5. Upload Media

```bash
curl -X POST http://localhost:8090/api/v1/media/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "memory_id=MEMORY_ID" \
  -F "file=@photo.jpg" \
  -F "display_order=1"
```

### 6. Purchase Shop Item

```bash
curl -X POST http://localhost:8090/api/v1/shop/purchase/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shop_item_id": 1,
    "quantity": 1
  }'
```

## 💾 Data Seeding

The project includes a comprehensive data seeding command:

```bash
# Seed with default data (20 users)
docker-compose exec mmdj_api python manage.py seed_data

# Seed with custom number of users
docker-compose exec mmdj_api python manage.py seed_data --users 50

# Clear existing data and reseed
docker-compose exec mmdj_api python manage.py seed_data --clear
```

### Seeded Data Includes:

- 1 admin user (`admin@admin.com` / `admin`)
- 20 regular users (configurable)
- 5 shop items (markers and themes)
- Sample locations with PostGIS geometry
- Memories with 1-1 location relationships
- Media files (Base64 encoded)
- User purchases and transaction history
- Memory likes and interactions

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8090/health/
```

### Admin Access

1. Visit http://localhost:8090/admin/
2. Login with `admin@admin.com` / `admin`
3. Manage users, locations, memories, and shop items

### API Documentation

1. Visit http://localhost:8090/api/docs/
2. Interactive Swagger UI for testing endpoints
3. Complete API schema documentation

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   docker-compose logs mmdj_db
   docker-compose restart mmdj_db
   ```

2. **Migration Issues**
   ```bash
   docker-compose exec mmdj_api python manage.py makemigrations
   docker-compose exec mmdj_api python manage.py migrate
   ```

3. **PostGIS Extension Error**
   ```bash
   docker-compose exec mmdj_db psql -U mmdj_user -d map_memories_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   ```

4. **Port Conflicts**
   ```bash
   # Check if ports are in use
   sudo lsof -i :8090
   sudo lsof -i :5433
   
   # Stop conflicting services
   docker-compose down
   ```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f mmdj_api
docker-compose logs -f mmdj_db
docker-compose logs -f mmdj_redis
```

## 🔧 Configuration

### Environment Variables

Create `.env` file for custom configuration:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_HOST=mmdj_db
DB_PORT=5432
DB_NAME=map_memories_db
DB_USER=mmdj_user
DB_PASSWORD=mmdj_password123
REDIS_URL=redis://mmdj_redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://your-frontend.com
```

### Django Settings

Key settings can be customized in `map_memories/settings.py`:

- File upload limits
- Pagination settings
- JWT token lifetime
- CORS settings
- Cache configuration

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Set production environment
export DEBUG=False
export SECRET_KEY=your-production-secret-key

# Use production database
export DATABASE_URL=postgresql://user:pass@prod-host:5432/prod_db
```

### 2. Security Checklist

- [ ] Change default secret key
- [ ] Set DEBUG=False
- [ ] Configure allowed hosts
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Regular database backups

### 3. Performance Optimization

- [ ] Enable Redis caching
- [ ] Configure CDN for media files
- [ ] Set up database connection pooling
- [ ] Enable compression in nginx
- [ ] Monitor and optimize database queries

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Create an issue in the repository
