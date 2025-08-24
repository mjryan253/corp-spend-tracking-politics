#!/usr/bin/env python3
"""
Script to help set up environment variables for the Corporate Spending Tracker.
"""

import os

def create_env_file():
    """Create a .env file with the current database configuration."""
    
    # Get current values or defaults
    db_host = input("Enter database host (default: jwst.domain.castle): ").strip() or "jwst.domain.castle"
    db_port = input("Enter database port (default: 5432): ").strip() or "5432"
    db_name = input("Enter database name (default: corp_spend_tracker): ").strip() or "corp_spend_tracker"
    db_user = input("Enter database user (default: postgres): ").strip() or "postgres"
    db_password = input("Enter database password: ").strip()
    
    if not db_password:
        print("Error: Database password is required!")
        return
    
    # Create .env file content
    env_content = f"""# Database Configuration
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}

# Django Configuration
SECRET_KEY=django-insecure-r55(7n1p8aad8d!)u_&6-4@!glt!ba!o93#%gajl(^8h^r9f#a
DEBUG=True
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print("You can now run: python setup_postgres.py")

if __name__ == "__main__":
    print("Setting up environment variables for Corporate Spending Tracker")
    print("=" * 60)
    create_env_file()
