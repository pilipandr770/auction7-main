from sqlalchemy.orm import relationship
from app.models.auction_participant import AuctionParticipant
from app import db
from sqlalchemy.dialects.sqlite import JSON


class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_participants = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    total_earnings = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    photos = db.Column(JSON, default=list)  # Поле для зберігання шляхів до фото у форматі JSON
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)  # Чи підтверджено отримання товару
    main_photo_idx = db.Column(db.Integer, default=0)  # Індекс головного фото

    # Відношення з AuctionParticipant
    participants = relationship(
        'AuctionParticipant', back_populates='auction', cascade='all, delete-orphan', lazy='dynamic'
    )

    def __init__(self, title, description, starting_price, seller_id, photos=None, main_photo_idx=None):
        self.title = title
        self.description = description
        self.starting_price = starting_price
        self.current_price = starting_price
        self.seller_id = seller_id
        self.photos = photos if photos else []
        self.main_photo_idx = main_photo_idx if main_photo_idx is not None else 0

    def add_participant(self, user):
        if not self.is_user_participant(user):
            new_participant = AuctionParticipant(auction_id=self.id, user_id=user.id)
            db.session.add(new_participant)
            self.total_participants += 1

    def is_user_participant(self, user):
        return self.participants.filter_by(user_id=user.id).count() > 0

    def decrease_price(self, entry_price):
        """
        Зменшує поточну ціну аукціону на задану суму.
        """
        self.current_price -= entry_price
        if self.current_price <= 0:
            self.current_price = 0
            self.close_auction()

    def close_auction(self, winner_id=None):
        """
        Закриває аукціон, встановлюючи статус як неактивний,
        та зберігає ID переможця, якщо вказано.
        """
        self.is_active = False
        if winner_id:
            self.winner_id = winner_id
        db.session.commit()

    def finalize_auction(self, buyer, seller):
        """
        Завершує аукціон:
        - Списує кошти з переможця (лише `current_price`).
        - Додає дохід до балансу продавця (всі вхідні внески + `current_price`).
        - Зберігає ID переможця.
        - Закриває аукціон.
        """
        # Розрахунок загального доходу продавця
        total_entry_payments = self.total_participants * self.starting_price * 0.01
        total_revenue = total_entry_payments + self.current_price

        # Перевірка, чи вистачає коштів у покупця
        if buyer.balance < self.current_price:
            raise ValueError("Недостатньо коштів для завершення аукціону.")

        # Списуємо тільки `current_price` з покупця
        buyer.deduct_balance(self.current_price)

        # Додаємо всю зароблену суму до балансу продавця
        seller.add_balance(total_revenue)

        # Закриваємо аукціон
        self.close_auction(winner_id=buyer.id)

    def add_to_earnings(self, amount):
        """
        Додає суму до заробітку аукціону.
        """
        self.total_earnings += amount
        db.session.commit()

    def charge_for_view(self, user, amount):
        """
        Списує суму з користувача за перегляд поточної ціни
        та додає її до заробітку аукціону.
        """
        if user.can_afford(amount):
            user.deduct_balance(amount)
            self.add_to_earnings(amount)
        else:
            raise ValueError("Недостатньо коштів для перегляду ціни.")

    def get_status(self):
        """
        Повертає статус аукціону як рядок ('Активний' або 'Закритий').
        """
        return 'Активний' if self.is_active else 'Закритий'

    def is_participation_allowed(self, user_balance, entry_price):
        """
        Перевіряє, чи дозволено користувачу брати участь в аукціоні.
        """
        if not self.is_active or user_balance < entry_price:
            return False
        return True

    def get_time_info(self):
        """
        Повертає інформацію про час створення та оновлення аукціону.
        """
        return {
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def reset_current_price(self):
        """
        Скидає поточну ціну до стартової.
        """
        self.current_price = self.starting_price

    def add_photos(self, photos):
        """
        Додає шляхи до фотографій у поле photos.
        :param photos: Список шляхів до фотографій.
        """
        if not self.photos:
            self.photos = []
        self.photos.extend(photos)
        db.session.commit()

    def get_main_photo(self):
        if self.photos and 0 <= (self.main_photo_idx or 0) < len(self.photos):
            return self.photos[self.main_photo_idx or 0]
        return self.photos[0] if self.photos else None
        
    def get_safe_photo(self, index=None):
        """
        Returns a safe photo path that exists in the file system.
        If the specified photo doesn't exist, returns a fallback image.
        
        :param index: Index of the photo to retrieve. If None, uses the main photo.
        :return: A valid photo path
        """
        import os
        from flask import current_app
        
        # Default fallback image
        fallback_image = 'images/default/no-image.png'
        
        # Get the photo path based on index or main photo
        if index is not None and self.photos and 0 <= index < len(self.photos):
            photo_path = self.photos[index]
        elif self.photos and 0 <= (self.main_photo_idx or 0) < len(self.photos):
            photo_path = self.photos[self.main_photo_idx or 0]
        elif self.photos and len(self.photos) > 0:
            photo_path = self.photos[0]
        else:
            return fallback_image
              # Check if file exists
        full_path = os.path.join(current_app.static_folder, photo_path)
        if os.path.isfile(full_path):
            return photo_path
        else:
            # Log the missing file
            print(f"Warning: Image file not found: {photo_path}")
            return fallback_image
            
    def get_participant(self, user_id):
        """
        Повертає об'єкт AuctionParticipant для цього аукціону та user_id, або None.
        """
        print(f"[DEBUG] Getting participant for auction ID: {self.id}, user ID: {user_id}")
        try:
            return self.participants.filter_by(user_id=user_id).first()
        except Exception as e:
            print(f"[ERROR] Failed to get participant: {e}")
            from app.models.auction_participant import AuctionParticipant
            return AuctionParticipant.query.filter_by(auction_id=self.id, user_id=user_id).first()
