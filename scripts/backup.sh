#!/bin/bash

# HR Recruitment System - Database Backup Script
# This script creates a database backup and optionally uploads it to AWS S3

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    source .env
fi

# Configuration
DB_NAME=${DB_NAME:-"hr_recruitment"}
DB_USER=${DB_USER:-"postgres"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_PASSWORD=${DB_PASSWORD:-"password"}

# AWS S3 bucket for backups (optional)
S3_BUCKET=${S3_BUCKET:-""}

# Backup directory
BACKUP_DIR=${BACKUP_DIR:-"/var/backups/hr_recruitment"}

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Set file name with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/hr_recruitment_$TIMESTAMP.sql"

# Set environment variable for PostgreSQL password
export PGPASSWORD=$DB_PASSWORD

echo "Starting database backup at $(date)"

# Create database backup
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -F c -b -v -f $BACKUP_FILE $DB_NAME

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Database backup completed successfully: $BACKUP_FILE"
    
    # Compress the backup file
    gzip -f $BACKUP_FILE
    COMPRESSED_FILE="$BACKUP_FILE.gz"
    echo "Backup compressed: $COMPRESSED_FILE"
    
    # Upload to S3 if bucket is configured
    if [ ! -z "$S3_BUCKET" ]; then
        echo "Uploading backup to S3 bucket: $S3_BUCKET"
        aws s3 cp $COMPRESSED_FILE s3://$S3_BUCKET/hr_recruitment_backups/
        
        if [ $? -eq 0 ]; then
            echo "Backup uploaded to S3 successfully"
        else
            echo "Failed to upload backup to S3"
        fi
    fi
    
    # Cleanup old backups (keep last 7 days)
    echo "Cleaning up old backups..."
    find $BACKUP_DIR -name "hr_recruitment_*.sql.gz" -type f -mtime +7 -delete
    
    echo "Backup process completed at $(date)"
else
    echo "Database backup failed!"
    exit 1
fi

# Clear password environment variable
unset PGPASSWORD
