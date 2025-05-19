from app import create_app, db

# Create the Flask application
app = create_app()

# Push an application context
with app.app_context():
    # Create the database tables
    db.create_all()
    print("Database tables created successfully.")
