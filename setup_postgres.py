#!/usr/bin/env python3
"""
Script to set up PostgreSQL database for the Corporate Spending Tracker.
Run this after installing PostgreSQL.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'jwst.domain.castle'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            database='postgres'  # Connect to default postgres database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Get database name from environment
        db_name = os.getenv('DB_NAME', 'corp_spend_tracker')
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE {db_name}')
            print("Database created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        
        print("\nPostgreSQL setup complete!")
        print("You can now run: python manage.py migrate")
        
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("\nPlease make sure:")
        print("1. PostgreSQL is installed")
        print("2. PostgreSQL service is running")
        print("3. The password for 'postgres' user is 'postgres'")
        print("\nPlease check:")
        print("1. The remote PostgreSQL server is running at jwst.domain.castle:5432")
        print("2. Your network can reach the remote server")
        print("3. The credentials (postgres/postgres) are correct")
        print("4. The database 'corp_spend_tracker' exists or you have permission to create it")
        
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    setup_database()
