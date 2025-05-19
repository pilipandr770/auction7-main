from flask import Blueprint, render_template, session, redirect, url_for, request
from flask_login import current_user
from blockchain_payments.payment_token_discount import get_user_discount
from app.models.auction import Auction
from app.utils.i18n_ui import ui_text

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    lang = session.get('lang', 'ua')
    auctions = Auction.query.filter_by(is_active=True).all()
    discount = None
    if current_user.is_authenticated and current_user.wallet_address:
        try:
            discount = get_user_discount(current_user.wallet_address)
        except Exception:
            discount = None
    if lang == 'en':
        return render_template('index_en.html', auctions=auctions, user_discount=discount, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('index_de.html', auctions=auctions, user_discount=discount, lang=lang, ui_text=ui_text)
    return render_template('index.html', auctions=auctions, user_discount=discount, lang=lang, ui_text=ui_text)

@main_bp.route('/en')
def index_en():
    # Deprecated: use index() with lang='en'
    return redirect(url_for('main.index'))

@main_bp.route('/de')
def index_de():
    # Deprecated: use index() with lang='de'
    return redirect(url_for('main.index'))

@main_bp.route('/privacy')
def privacy():
    lang = session.get('lang', 'ua')
    if lang == 'en':
        return render_template('privacy_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('privacy_de.html', lang=lang, ui_text=ui_text)
    return render_template('privacy.html', lang=lang, ui_text=ui_text)

@main_bp.route('/impressum')
def impressum():
    lang = session.get('lang', 'ua')
    if lang == 'en':
        return render_template('impressum_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('impressum_de.html', lang=lang, ui_text=ui_text)
    return render_template('impressum.html', lang=lang, ui_text=ui_text)

@main_bp.route('/contacts')
def contacts():
    lang = session.get('lang', 'ua')
    if lang == 'en':
        return render_template('contacts_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('contacts_de.html', lang=lang, ui_text=ui_text)
    return render_template('contacts.html', lang=lang, ui_text=ui_text)

@main_bp.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['ua', 'en', 'de']:
        session['lang'] = lang
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            current_user.language = lang
            from app import db
            db.session.commit()
    return redirect(request.referrer or url_for('main.index'))
