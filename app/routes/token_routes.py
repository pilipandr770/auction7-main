from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.utils.i18n_ui import ui_text
from app import db
from app.models.token import Token

# Create token blueprint
token_bp = Blueprint('token', __name__)

@token_bp.route('/token-info')
def token_info():
    lang = session.get('lang', 'ua')
    if lang == 'en':
        return render_template('token_info_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('token_info_de.html', lang=lang, ui_text=ui_text)
    return render_template('token_info.html', lang=lang, ui_text=ui_text)

@token_bp.route('/token-buy', methods=['GET', 'POST'])
@login_required
def buy():
    lang = session.get('lang', 'ua')
    token_purchased = False
    error = None
    
    if request.method == 'POST':
        # Simulate token purchase (in a real app, you'd have payment processing here)
        try:
            # Check if user already has tokens
            token = Token.query.filter_by(user_id=current_user.id).first()
            
            if token:
                # Add to existing tokens
                token.amount += 1
            else:
                # Create new token record
                token = Token(user_id=current_user.id, amount=1)
                db.session.add(token)
                
            db.session.commit()
            token_purchased = True
            
            success_message = {
                'ua': 'Токен AUKTO успішно придбано! Тепер ви можете брати участь у ДАО.',
                'en': 'AUKTO token successfully purchased! You can now participate in the DAO.',
                'de': 'AUKTO-Token erfolgreich gekauft! Sie können jetzt an der DAO teilnehmen.'
            }
            flash(success_message.get(lang, success_message['en']))
            
        except Exception as e:
            error = {
                'ua': 'Помилка при придбанні токена: ' + str(e),
                'en': 'Error purchasing token: ' + str(e),
                'de': 'Fehler beim Kauf des Tokens: ' + str(e)
            }[lang]
    
    if lang == 'en':
        return render_template('token_buy_en.html', token_purchased=token_purchased, error=error, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('token_buy_de.html', token_purchased=token_purchased, error=error, lang=lang, ui_text=ui_text)
    return render_template('token_buy.html', token_purchased=token_purchased, error=error, lang=lang, ui_text=ui_text)

@token_bp.route('/token-airdrop', methods=['GET', 'POST'])
def airdrop():
    lang = session.get('lang', 'ua')
    airdrop_sent = False
    error = None
    
    if request.method == 'POST':
        wallet_address = request.form.get('wallet_address')
        if wallet_address and wallet_address.startswith('0x') and len(wallet_address) == 42:
            try:
                if current_user.is_authenticated:
                    # Check if user already has tokens
                    token = Token.query.filter_by(user_id=current_user.id).first()
                    
                    if token:
                        # Add to existing tokens
                        token.amount += 1
                        token.token_address = wallet_address  # Update wallet address
                    else:
                        # Create new token record with wallet
                        token = Token(user_id=current_user.id, amount=1, token_address=wallet_address)
                        db.session.add(token)
                        
                    db.session.commit()
                
                # Set success flag
                airdrop_sent = True
                
                if current_user.is_authenticated:
                    success_message = {
                        'ua': 'Токени AUKTO відправлені на ваш гаманець! Тепер ви можете брати участь у ДАО.',
                        'en': 'AUKTO tokens sent to your wallet! You can now participate in the DAO.',
                        'de': 'AUKTO-Token an Ihr Wallet gesendet! Sie können jetzt an der DAO teilnehmen.'
                    }
                    flash(success_message.get(lang, success_message['en']))
                
            except Exception as e:
                error = {
                    'ua': 'Помилка при обробці airdrop: ' + str(e),
                    'en': 'Error processing airdrop: ' + str(e),
                    'de': 'Fehler bei der Verarbeitung des Airdrops: ' + str(e)
                }[lang]
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
