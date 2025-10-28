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
   python -m venv venv
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

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

## Features

- **Bidirectional Translation**: Shuar ↔ Spanish translation with automatic language detection
- **Phonological Analysis**: Complete integration with Shuar phonological system (3 vocal types)
- **Community Feedback**: Rating and suggestion system for translation improvements
- **Expert Panel**: Administrative interface for linguistic experts
- **Morphological Analysis**: Support for compound words and morphological decomposition

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