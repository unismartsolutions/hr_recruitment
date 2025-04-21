hr_recruitment/
├── app/
│   ├── __init__.py           # Flask application initialization
│   ├── config.py             # Configuration settings
│   ├── models.py             # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes
│   │   ├── candidates.py     # Candidate management routes
│   │   └── search.py         # Search functionality routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py   # Authentication logic
│   │   ├── cv_service.py     # CV processing logic 
│   │   ├── gpt_service.py    # OpenAI GPT integration
│   │   └── search_service.py # Search functionality
│   ├── static/
│   │   ├── css/              # Stylesheets
│   │   ├── js/               # JavaScript files
│   │   └── uploads/          # Folder for uploaded CVs
│   └── templates/            # HTML templates
│       ├── base.html         # Base template
│       ├── login.html        # Login page
│       ├── upload.html       # CV upload page
│       └── search.html       # Search page
├── scripts/
│   ├── backup.sh             # Database backup script
│   └── db_init.sql           # Database initialization script
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
├── .env                      # Environment variables (not in version control)
└── README.md                 # Project documentation
```
