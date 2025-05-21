"""
Translation dictionary for system messages (Ukrainian, English, German)
"""

messages = {
    'login_error': {
        'ua': "Неправильний email або пароль",
        'en': "Incorrect email or password",
        'de': "Falsche E-Mail або Passwort"
    },
    'login_success': {
        'ua': "Успішний вхід",
        'en': "Login successful",
        'de': "Erfolgreich eingeloggt"
    },
    'not_authorized': {
        'ua': "Неавторизований доступ",
        'en': "Unauthorized access",
        'de': "Nicht autorisierter Zugriff"
    },
    'user_not_found': {
        'ua': "Користувача не знайдено",
        'en': "User not found",
        'de': "Benutzer nicht gefunden"
    },
    'auction_not_found': {
        'ua': "Аукціон не знайдено.",
        'en': "Auction not found.",
        'de': "Auktion nicht gefunden."
    },
    'already_viewed_price': {
        'ua': "Ви вже переглядали поточну ціну цього аукціону.",
        'en': "You have already viewed the current price of this auction.",
        'de': "Sie haben den aktuellen Preis dieser Auktion bereits angesehen."
    },
    'not_enough_balance': {
        'ua': "Недостатньо коштів на балансі для перегляду ціни.",
        'en': "Not enough balance to view the price.",
        'de': "Nicht genügend Guthaben, um den Preis anzuzeigen."
    },
    'user_exists': {
        'ua': "Користувач з такою електронною поштою вже існує.",
        'en': "User with this email already exists.",
        'de': "Benutzer mit dieser E-Mail existiert bereits."
    },    'username_exists': {
        'ua': "Користувач з таким іменем вже існує. Будь ласка, виберіть інше ім'я.",
        'en': "User with this username already exists. Please choose another username.",
        'de': "Benutzer mit diesem Benutzernamen existiert bereits. Bitte wählen Sie einen anderen Benutzernamen."
    },    'register_error': {
        'ua': "Помилка при реєстрації. Будь ласка, спробуйте ще раз.",
        'en': "Registration error. Please try again.",
        'de': "Registrierungsfehler. Bitte versuchen Sie es erneut."
    },    'register_seller_success': {
        'ua': "Реєстрація продавця успішна! Очікуйте перевірки адміністратором.",
        'en': "Seller registration successful! Waiting for admin verification.",
        'de': "Verkäuferregistrierung erfolgreich! Warten auf Überprüfung durch den Administrator."
    },    'verification_doc_required': {
        'ua': "Документ для верифікації обов'язковий.",
        'en': "Verification document is required.",
        'de': "Verifizierungsdokument ist erforderlich."
    },
    'all_fields_required': {
        'ua': "Усі поля обов'язкові для заповнення.",
        'en': "All fields are required.",
        'de': "Alle Felder sind erforderlich."
    },
    'user_type_invalid': {
        'ua': "Недійсний тип користувача.",
        'en': "Invalid user type.",
        'de': "Ungültiger Benutzertyp."
    },
    'register_success': {
        'ua': "Реєстрація успішна!",
        'en': "Registration successful!",
        'de': "Registrierung erfolgreich!"
    },
    'register_buyer_success': {
        'ua': "Реєстрація покупця успішна!",
        'en': "Buyer registration successful!",
        'de': "Käuferregistrierung erfolgreich!"
    },
    'logout_success': {
        'ua': "Ви успішно вийшли з системи.",
        'en': "You have successfully logged out.",
        'de': "Sie haben sich erfolgreich abgemeldet."
    },    'user_role_undefined': {
        'ua': "Тип користувача не визначено.",
        'en': "User role is undefined.",
        'de': "Benutzerrolle ist nicht definiert."
    },    'already_participating': {
        'ua': "Ви вже є учасником аукціону.",
        'en': "You are already participating in this auction.",
        'de': "Sie nehmen bereits an dieser Auktion teil."
    },
    'not_participant': {
        'ua': "Тільки учасники можуть переглядати поточну ціну.",
        'en': "Only participants can view the current price.",
        'de': "Nur Teilnehmer können den aktuellen Preis einsehen."
    },    'view_updated': {
        'ua': "Ціна показана. Дякуємо за оплату.",
        'en': "Price shown. Thank you for your payment.",
        'de': "Preis angezeigt. Vielen Dank für Ihre Zahlung."
    }
}

def get_message(key, lang='ua'):
    return messages.get(key, {}).get(lang, messages.get(key, {}).get('ua', ''))
