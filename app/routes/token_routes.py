from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.utils.i18n_ui import ui_text

# Створюємо blueprint для токен-сторінок

token_bp = Blueprint('token', __name__)

@token_bp.route('/token-info')
def token_info():
    lang = session.get('lang', 'ua')
    if lang == 'en':
        return render_template('token_info_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('token_info_de.html', lang=lang, ui_text=ui_text)
    return render_template('token_info.html', lang=lang, ui_text=ui_text)

@token_bp.route('/token-buy')
def buy():
    lang = session.get('lang', 'ua')
    if lang == 'en':
        return render_template('token_buy_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('token_buy_de.html', lang=lang, ui_text=ui_text)
    return render_template('token_buy.html', lang=lang, ui_text=ui_text)

@token_bp.route('/token-airdrop', methods=['GET', 'POST'])
def airdrop():
    lang = session.get('lang', 'ua')
    airdrop_sent = False
    error = None
    if request.method == 'POST':
        wallet_address = request.form.get('wallet_address')
        if wallet_address and wallet_address.startswith('0x') and len(wallet_address) == 42:
            # Тут має бути логіка надсилання токенів (airdrop)
            # Для демо просто показуємо успіх
            airdrop_sent = True
        else:
            error = {
                'ua': 'Введіть коректну адресу гаманця Polygon.',
                'en': 'Enter a valid Polygon wallet address.',
                'de': 'Geben Sie eine gültige Polygon-Wallet-Adresse ein.'
            }[lang]
    if lang == 'en':
        return render_template('token_airdrop_en.html', airdrop_sent=airdrop_sent, error=error, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('token_airdrop_de.html', airdrop_sent=airdrop_sent, error=error, lang=lang, ui_text=ui_text)
    return render_template('token_airdrop.html', airdrop_sent=airdrop_sent, error=error, lang=lang, ui_text=ui_text)
