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
    # ...add more as needed...
}

def get_message(key, lang='ua'):
    return messages.get(key, {}).get(lang, messages.get(key, {}).get('ua', ''))
