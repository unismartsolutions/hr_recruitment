# HR Recruitment System - Local Setup Guide

This guide provides comprehensive instructions for setting up and running the HR Recruitment System locally on your machine for development and testing.

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **PostgreSQL 12+** - [Download PostgreSQL](https://www.postgresql.org/download/)
3. **Git** (optional) - For version control
4. **OpenAI API Key** - Sign up at [OpenAI](https://platform.openai.com/) and get an API key

Verify your installations:
```bash
python --version  # or python3 --version on some systems
psql --version
```

## Step 1: Project Setup

### Clone or Download the Project

Either clone the repository (if using Git) or download and extract the project files to your local machine.

```bash
git clone https://your-repository-url.git hr_recruitment
cd hr_recruitment
```

If you're starting from scratch, create the directory structure as shown in the project documentation.

## Step 2: Set Up Virtual Environment

Create and activate a virtual environment to isolate project dependencies:

### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see the virtual environment name in your terminal prompt, indicating it's active.

## Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install all necessary dependencies including Flask, SQLAlchemy, PyPDF2, and the OpenAI client.

## Step 4: Set Up PostgreSQL Database

### Create a New Database:

#### For Windows:
```bash
# Using psql command line
psql -U postgres
```

#### For macOS:
```bash
psql postgres
```

#### For Linux:
```bash
sudo -u postgres psql
```

### Execute the Following SQL Commands:

```sql
CREATE DATABASE hr_recruitment;
CREATE USER hr_user WITH PASSWORD 'test123';
GRANT ALL PRIVILEGES ON DATABASE hr_recruitment TO hr_user;
\q
```

Replace 'your_secure_password' with a strong password.

## Step 5: Initialize the Database Schema

Use the provided database initialization script:

```bash
psql -U hr_user -d hr_recruitment -f scripts/db_init.sql
```

If you encounter connection issues, you might need to specify the host:

```bash
psql -h localhost -U hr_user -d hr_recruitment -f scripts/db_init.sql
```

## Step 6: Configure Environment Variables

Create a `.env` file in the project root directory:

```
# Flask configuration
SECRET_KEY=generate_a_secure_random_key_here
FLASK_APP=run.py
FLASK_ENV=development

# Database configuration
DATABASE_URL=postgresql://hr_user:your_secure_password@localhost/hr_recruitment

# OpenAI API configuration
OPENAI_API_KEY=your_openai_api_key

# Upload folder (relative path for local development)
UPLOAD_FOLDER=app/static/uploads
```

Replace the placeholder values with your actual configuration:
- Generate a secret key with: `python -c "import secrets; print(secrets.token_hex(16))"`
- Use the PostgreSQL password you created earlier
- Add your OpenAI API key

## Step 7: Initialize the Flask Application

Initialize the application with:

```bash
# Make sure your virtual environment is activated
flask init-db
```

This command creates an admin user with default credentials:
- Username: `admin`
- Password: `admin123`

## Step 8: Create Uploads Directory

Make sure the uploads directory exists:

```bash
# For Windows
mkdir -p app\static\uploads

# For macOS/Linux
mkdir -p app/static/uploads
```

## Step 9: Run the Application

Start the Flask development server:

```bash
flask run
```

You should see output similar to:
```
* Serving Flask app 'run.py'
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## Step 10: Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

Log in with the default admin credentials:
- Username: `admin`
- Password: `admin123`

**IMPORTANT**: Change the default admin password after your first login!

## Testing the Features

### Upload a CV:
1. After login, you'll be on the CV upload page
2. Drag and drop a PDF resume or click "Select File" to browse
3. Wait while the system processes and extracts information
4. Review and edit the extracted information
5. Click "Save Candidate" to store the data

### Search for Candidates:
1. Navigate to the Search page from the navigation bar
2. Use the search bar for basic searches
3. Click "Advanced Filters" for more detailed search options
4. Filter by skills, experience level, industry, etc.
5. Click "Search" to find matching candidates

### Job Matching:
1. On the Search page, switch to the "Job Matching" tab
2. Enter detailed job requirements in the text area
3. Click "Find Matching Candidates" to get a ranked list
4. Review candidates with their match scores

## Troubleshooting

### Database Connection Issues:
- Verify PostgreSQL is running: `pg_isready`
- Check your DATABASE_URL in the .env file
- Ensure the database user has proper permissions

### OpenAI API Issues:
- Verify your API key is correct and has sufficient credits
- Check for network connectivity issues

### File Upload Issues:
- Make sure the upload directory exists and is writable
- Check that the file is a valid PDF
- Verify the file size is within limits (16MB by default)

### Missing Modules:
If you get "module not found" errors, install the missing package:
```bash
pip install <package_name>
```

### Console Logs:
- Check the Flask console output for errors
- Set `FLASK_ENV=development` in your .env file for detailed logs

## Additional Commands

### Creating a New User:

```bash
# Make sure your virtual environment is activated
export FLASK_APP=run.py  # On Windows: set FLASK_APP=run.py
flask create-user
```

Follow the prompts to enter username, email, and password.

### Database Backup:

Back up your local database with:

```bash
pg_dump -U hr_user -F c -b -v -f hr_recruitment_backup.sql hr_recruitment
```

## Next Steps

After successfully testing locally, you can deploy to AWS EC2 following the deployment guide provided with the project.

## Conclusion

You should now have a fully functional HR Recruitment System running locally. This setup is ideal for development and testing before moving to production.

If you encounter any issues, refer to the project documentation or check the Flask and PostgreSQL logs for more details.
