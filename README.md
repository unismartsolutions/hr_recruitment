# HR Recruitment System

A comprehensive HR recruitment system with Python Flask backend, HTML/JS frontend, and PostgreSQL database. The system extracts information from CVs using OpenAI GPT models and provides advanced search capabilities for finding the best candidates.

## Features

- **User Authentication**: Secure login system
- **CV Upload & Processing**: 
  - PDF CV upload and processing
  - Automatic extraction of candidate information
  - Integration with OpenAI GPT-4o-mini for intelligent CV parsing
  - Extraction of skills, experience level, education, certifications, and more
- **Advanced Search**:
  - Search by skills, experience level, industry, certifications, etc.
  - Full-text search across all candidate data
- **Job Matching**:
  - AI-powered matching of candidates to job requirements
  - Intelligent ranking system for candidates based on job fit
- **Database Management**:
  - PostgreSQL database for reliable data storage
  - Automatic database backups
  - AWS S3 backup integration

## Technical Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript (Bootstrap 5)
- **Database**: PostgreSQL
- **AI Integration**: OpenAI GPT-4o-mini
- **PDF Processing**: PyPDF2
- **Deployment**: AWS EC2, Nginx, Gunicorn

## System Architecture

```
hr_recruitment/
├── app/                       # Flask application
│   ├── models.py              # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic
│   ├── static/                # Static assets
│   └── templates/             # HTML templates
├── scripts/                   # Utility scripts
│   ├── backup.sh              # Database backup
│   └── db_init.sql            # Database initialization
└── requirements.txt           # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 13+
- OpenAI API key

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://your-repository-url.git
   cd hr_recruitment
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a PostgreSQL database:
   ```bash
   createdb hr_recruitment
   ```

5. Initialize the database:
   ```bash
   psql -U your_user -d hr_recruitment -f scripts/db_init.sql
   ```

6. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_secure_secret_key
   DATABASE_URL=postgresql://username:password@localhost/hr_recruitment
   OPENAI_API_KEY=your_openai_api_key
   ```

7. Initialize the Flask application:
   ```bash
   export FLASK_APP=run.py
   flask init-db
   ```

8. Run the development server:
   ```bash
   flask run
   ```

9. Access the application at http://localhost:5000

### Production Deployment

For detailed production deployment instructions, see the [AWS EC2 Deployment Guide](deployment-guide.md).

## API Endpoints

### Authentication
- `GET /login` - Render login page
- `POST /login` - Process login
- `GET /logout` - Log out current user

### Candidate Management
- `GET /upload` - Render CV upload page
- `POST /process-resume` - Process uploaded CV
- `POST /save-candidate` - Save candidate to database
- `GET /candidates/<id>` - Get candidate details
- `DELETE /candidates/<id>` - Delete candidate

### Search
- `GET /search` - Render search page
- `POST /api/search` - Search candidates
- `POST /api/match-job` - Match candidates to job requirements

## Database Backup

A backup script is provided in `scripts/backup.sh`. This script:
- Creates a compressed backup of the PostgreSQL database
- Optionally uploads the backup to an AWS S3 bucket
- Removes backups older than 7 days

To set up automated daily backups, add a cron job:
```bash
0 2 * * * /path/to/hr_recruitment/scripts/backup.sh >> /var/log/hr_backup.log 2>&1
```

## Security Considerations

- All passwords are hashed using Werkzeug's security functions
- SQL injection is prevented by using SQLAlchemy's ORM
- CSRF protection is enabled by default in Flask-WTF
- User input is validated on both client and server sides
- File uploads are restricted to PDF format and size-limited

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Bootstrap](https://getbootstrap.com/)
- [OpenAI](https://openai.com/)
- [PyPDF2](https://github.com/py-pdf/pypdf)
