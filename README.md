# Shuar Chicham Interactive Translator

A web-based platform designed to preserve and promote the Shuar language by providing bidirectional translation capabilities between Shuar and Spanish.

## Architecture

This project follows **Clean Architecture** principles with **Domain-Driven Design (DDD)** patterns organized by features:

```
app/
├── core/                    # Core application components
│   ├── shared/             # Shared configuration and components
│   │   ├── config.py       # Application settings
│   │   ├── container.py    # Dependency injection container
│   │   └── exceptions.py   # Shared exceptions
│   ├── utils/              # Utility functions
│   │   ├── logger.py       # Logging configuration
│   │   └── validators.py   # Validation utilities
│   └── infrastructure/     # Core infrastructure
│       └── supabase_client.py  # Database client
└── features/               # Feature modules
    ├── translation/        # Translation feature
    │   ├── domain/         # Business logic and rules
    │   ├── application/    # Use cases and DTOs
    │   ├── infrastructure/ # Repository implementations
    │   └── presentation/   # API controllers and schemas
    ├── feedback/           # Community feedback feature
    └── admin/              # Expert administration feature
```

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with Supabase
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Supabase Auth
- **Dependency Injection**: dependency-injector
- **Testing**: pytest

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shuar-translator
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

5. **Set up database**
   ```bash
   # Run these SQL files in your Supabase SQL editor in order:
   # 1. app/core/infrastructure/database/migrations/000_create_phonological_system.sql
   # 2. app/core/infrastructure/database/migrations/001_create_translation_tables.sql
   # 3. app/core/infrastructure/database/migrations/002_create_dictionary_tables.sql  
   # 4. app/core/infrastructure/database/migrations/003_seed_sample_data.sql
   ```

6. **Run the application**
   ```bash
   python3 main.py
   # Or use the smart startup script:
   python3 run.py
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

## Features

- **Comprehensive Dictionary**: Complete Shuar-Spanish dictionary with 20+ sample words
- **Bidirectional Translation**: Shuar ↔ Spanish translation with automatic language detection
- **Phonological Analysis**: Complete integration with Shuar phonological system (3 vocal types)
- **Linguistic Detail**: Morphological analysis, IPA pronunciation, syllable breakdown
- **Cultural Context**: Semantic fields, cultural significance, usage examples
- **Dialectal Variants**: Support for Achuar, Shiwiar and other Shuar dialects
- **Community Feedback**: Rating and suggestion system for translation improvements
- **Expert Panel**: Administrative interface for linguistic experts
- **Fuzzy Search**: Advanced search with similarity matching for partial words

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/
isort src/
```

### Type Checking
```bash
mypy src/
```

## API Endpoints

### Translation
- `POST /api/translate` - Translate text between Shuar and Spanish
- `GET /api/suggestions/{word}` - Get phonologically similar words

### Feedback
- `POST /api/feedback` - Submit translation feedback
- `GET /api/translations/{id}/feedback` - Get feedback for a translation

### Admin (Expert Panel)
- `POST /api/admin/words` - Add new vocabulary
- `GET /api/admin/pending-feedback` - Review pending feedback
- `PUT /api/admin/feedback/{id}/approve` - Approve/reject feedback

## Contributing

This project aims to preserve the Shuar language through technology. Contributions from Shuar speakers and linguistic experts are especially welcome.

## License

[Add appropriate license]