from app import create_app, db
from app.models.user import User

def list_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print("\n----- Список всех пользователей в базе данных -----")
        for user in users:
            print(f"Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}, Type: {user.user_type}")
        print("------------------------------------------------\n")

if __name__ == "__main__":
    list_users()
