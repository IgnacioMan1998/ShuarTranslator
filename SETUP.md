# Shuar Chicham Translator - Setup Instructions

## Prerequisites

- Python 3.11+
- Supabase account and project
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shuar-translator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   SECRET_KEY=your-secret-key
   ```

5. **Set up database**
   
   Run the migration SQL in your Supabase SQL editor:
   ```bash
   # Copy content from app/core/infrastructure/database/migrations/001_create_translation_tables.sql
   # and execute in Supabase SQL editor
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

## API Endpoints

### Translation
- `POST /api/translate` - Translate text
- `GET /api/translate/similar/{word}` - Find similar words
- `GET /api/translate/detailed/{word}` - Get detailed translation

### Feedback
- `POST /api/feedback/submit` - Submit feedback
- `GET /api/feedback/translation/{id}` - Get translation feedback

### Admin
- `POST /api/admin/words` - Add new word
- `GET /api/admin/pending-feedback` - Get pending feedback
- `PUT /api/admin/feedback/{id}/review` - Review feedback

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

```bash
pytest
```

## Project Structure

The project follows Clean Architecture with DDD:

```
app/
├── core/                    # Core components
│   ├── shared/             # Configuration, container, exceptions
│   ├── utils/              # Validators, logger
│   └── infrastructure/     # Supabase client, migrations
└── features/               # Feature modules
    ├── translation/        # Translation feature
    ├── feedback/           # Feedback feature
    └── admin/              # Admin feature
```

Each feature follows Clean Architecture layers:
- `domain/` - Entities, repositories (interfaces), services
- `application/` - Use cases, DTOs
- `infrastructure/` - Repository implementations
- `presentation/` - API controllers, schemas

## Key Features Implemented

✅ **Translation Engine**
- Bidirectional Shuar ↔ Spanish translation
- Automatic language detection
- Phonological analysis (3 vocal types)
- Morphological analysis
- Similarity-based word suggestions

✅ **Community Feedback**
- Rating system (1-5 stars)
- Comments and suggestions
- Native speaker verification
- Expert review workflow

✅ **Expert Administration**
- Word management with phonological data
- Feedback review and approval
- Bulk import capabilities
- Analytics and reporting

✅ **Technical Architecture**
- Clean Architecture + DDD
- FastAPI with async support
- Supabase PostgreSQL integration
- Comprehensive error handling
- Structured logging
- Dependency injection

## Next Steps

1. **Database Setup**: Execute the migration SQL in Supabase
2. **Data Import**: Use admin endpoints to import existing Shuar vocabulary
3. **Testing**: Run the test suite and add integration tests
4. **Deployment**: Configure for production deployment
5. **Frontend**: Build a web interface for the API

## Contributing

This project aims to preserve the Shuar language through technology. Contributions from Shuar speakers and linguistic experts are especially welcome.

## Support

For questions or issues, please refer to the API documentation at `/docs` or check the logs for detailed error information.