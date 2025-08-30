# Makefile for the Corporate Spending Tracker

# Default command
all: help

# Docker commands
up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

# Django management commands
shell:
	docker-compose exec backend python manage.py shell

test:
	docker-compose exec backend python manage.py test data_collection

test-ingestion:
	docker-compose exec backend python manage.py test_ingestion

sample-data:
	docker-compose exec backend python manage.py create_sample_data

ingest-data:
	docker-compose exec backend python manage.py ingest_data

# Utility commands
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

help:
	@echo "Available commands:"
	@echo "  make up              - Start the application with Docker"
	@echo "  make down            - Stop the application"
	@echo "  make logs            - View the application logs"
	@echo "  make shell           - Access the Django shell"
	@echo "  make test            - Run the backend tests"
	@echo "  make test-ingestion  - Test the data ingestion pipeline"
	@echo "  make sample-data     - Create sample data"
	@echo "  make ingest-data     - Ingest real data from sources"
	@echo "  make clean           - Remove Python cache files"