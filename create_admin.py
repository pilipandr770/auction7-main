from app import create_app, db
from app.models.user import User
import sys

def create_admin(email, username, password):
    app = create_app()
    with app.app_context():
        try:
            # Проверяем, существует ли пользователь с таким email
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Если пользователь существует, делаем его админом
                user.is_admin = True
                user.user_type = "admin"
                print(f"Пользователь {email} обновлен до администратора")
                # Сохраняем изменения
                db.session.commit()
                print("Операция успешно выполнена")
                return
                
            # Проверяем, существует ли пользователь с таким username
            existing_username = User.query.filter_by(username=username).first()
            if existing_username:
                print(f"ОШИБКА: Имя пользователя '{username}' уже занято!")
                print("Пожалуйста, используйте другое имя пользователя.")
                return
                
            # Создаем нового админа
            admin = User(username=username, 
                        email=email, 
                        password=password, 
                        user_type="admin", 
                        is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print(f"Создан новый администратор с email: {email}")
            print("Операция успешно выполнена")
            
        except Exception as e:
            db.session.rollback()
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python create_admin.py email username password")
        sys.exit(1)
    
    email = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    
    create_admin(email, username, password)
