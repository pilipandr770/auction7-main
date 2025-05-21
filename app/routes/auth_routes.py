from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models.user import User
from app import db
from app.utils.i18n_messages import get_message
from flask import session
from app.utils.i18n_ui import ui_text

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Перевірка користувача
        user = User.query.filter_by(email=email).first()

        lang = session.get('lang', 'ua')

        if not user or not user.check_password(password):
            flash(get_message('login_error', lang), 'error')
            return redirect(url_for('auth.login'))

        # Авторизація користувача
        login_user(user)
        flash(get_message('login_success', lang), 'success')

        # Перевірка типу користувача (user_type)
        if user.user_type == "admin":
            return redirect(url_for('admin.admin_dashboard'))  # Виправлений шлях
        elif user.user_type == "seller":
            return redirect(url_for('user.seller_dashboard', email=user.email))
        elif user.user_type == "buyer":
            return redirect(url_for('user.buyer_dashboard', email=user.email))
        else:
            flash(get_message('user_role_undefined', lang), 'error')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html', lang=session.get('lang', 'ua'), ui_text=ui_text)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')  # "seller", "buyer" або "admin"

        lang = session.get('lang', 'ua')

        if not email or not username or not password or not user_type:
            flash(get_message('all_fields_required', lang), 'error')
            return redirect(url_for('auth.register'))

        # Перевірка, чи email вже існує
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash(get_message('user_exists', lang), 'error')
            return redirect(url_for('auth.register'))

        # Перевірка типу користувача
        if user_type not in ['buyer', 'seller', 'admin']:
            flash(get_message('user_type_invalid', lang), 'error')
            return redirect(url_for('auth.register'))

        # Створення нового користувача
        user = User(username=username, email=email, password=password, user_type=user_type)
        if user_type == "admin":
            user.is_admin = True  # Позначаємо адміністратора
        db.session.add(user)
        db.session.commit()

        flash(get_message('register_success', lang), 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', lang=session.get('lang', 'ua'), ui_text=ui_text)


@auth_bp.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        lang = session.get('lang', 'ua')
        flash(get_message('logout_success', lang), 'success')
    else:
        lang = session.get('lang', 'ua')
        flash(get_message('not_authorized', lang), 'error')
    return redirect(url_for('auth.login'))

from werkzeug.utils import secure_filename
from app.forms.buyer_register_form import BuyerRegisterForm
from app.forms.seller_register_form import SellerRegisterForm
import os

@auth_bp.route('/choose-role')
def choose_role():
    lang = session.get('lang', 'ua')
    if lang == 'en':
        return render_template('auth/choose_role_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('auth/choose_role_de.html', lang=lang, ui_text=ui_text)
    return render_template('auth/choose_role.html', lang=lang, ui_text=ui_text)

@auth_bp.route('/register/buyer', methods=['GET', 'POST'])
def register_buyer():
    form = BuyerRegisterForm()
    lang = session.get('lang', 'ua')
    if form.validate_on_submit():
        # Перевірка, чи email вже існує
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash(get_message('user_exists', lang), 'error')
            if lang == 'en':
                return render_template('auth/register_buyer_en.html', form=form, lang=lang, ui_text=ui_text)
            elif lang == 'de':
                return render_template('auth/register_buyer_de.html', form=form, lang=lang, ui_text=ui_text)
            return render_template('auth/register_buyer.html', form=form, lang=lang, ui_text=ui_text)
        
        # Перевірка, чи username вже існує
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash(get_message('username_exists', lang), 'error')
            if lang == 'en':
                return render_template('auth/register_buyer_en.html', form=form, lang=lang, ui_text=ui_text)
            elif lang == 'de':
                return render_template('auth/register_buyer_de.html', form=form, lang=lang, ui_text=ui_text)
            return render_template('auth/register_buyer.html', form=form, lang=lang, ui_text=ui_text)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            user_type='buyer',
            language=lang
        )
        db.session.add(user)
        db.session.commit()
        flash(get_message('register_buyer_success', lang), 'success')
        return redirect(url_for('auth.login'))
    
    if lang == 'en':
        return render_template('auth/register_buyer_en.html', form=form, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('auth/register_buyer_de.html', form=form, lang=lang, ui_text=ui_text)
    return render_template('auth/register_buyer.html', form=form, lang=lang, ui_text=ui_text)

@auth_bp.route('/register/seller', methods=['GET', 'POST'])
def register_seller():
    form = SellerRegisterForm()
    lang = session.get('lang', 'ua')
    if form.validate_on_submit():
        # Перевірка, чи email вже існує
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash(get_message('user_exists', lang), 'error')
            if lang == 'en':
                return render_template('auth/register_seller_en.html', form=form, lang=lang, ui_text=ui_text)
            elif lang == 'de':
                return render_template('auth/register_seller_de.html', form=form, lang=lang, ui_text=ui_text)
            return render_template('auth/register_seller.html', form=form, lang=lang, ui_text=ui_text)
        
        # Перевірка, чи username вже існує
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash(get_message('username_exists', lang), 'error')
            if lang == 'en':
                return render_template('auth/register_seller_en.html', form=form, lang=lang, ui_text=ui_text)
            elif lang == 'de':
                return render_template('auth/register_seller_de.html', form=form, lang=lang, ui_text=ui_text)
            return render_template('auth/register_seller.html', form=form, lang=lang, ui_text=ui_text)
        
        file = form.verification_document.data
        if not file:
            flash(get_message('verification_doc_required', lang), 'error')
            if lang == 'en':
                return render_template('auth/register_seller_en.html', form=form, lang=lang, ui_text=ui_text)
            elif lang == 'de':
                return render_template('auth/register_seller_de.html', form=form, lang=lang, ui_text=ui_text)
            return render_template('auth/register_seller.html', form=form, lang=lang, ui_text=ui_text)
            
        try:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join('app', 'static', 'uploads', 'verify')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                user_type='seller',
                language=lang,
                verification_document=filepath,
                is_verified=False
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash(get_message('register_seller_success', lang), 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f"Error in seller registration: {e}")
            flash(get_message('register_error', lang), 'error')
            if lang == 'en':
                return render_template('auth/register_seller_en.html', form=form, lang=lang, ui_text=ui_text)
            elif lang == 'de':
                return render_template('auth/register_seller_de.html', form=form, lang=lang, ui_text=ui_text)
            return render_template('auth/register_seller.html', form=form, lang=lang, ui_text=ui_text)
            
    if lang == 'en':
        return render_template('auth/register_seller_en.html', form=form, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('auth/register_seller_de.html', form=form, lang=lang, ui_text=ui_text)
    return render_template('auth/register_seller.html', form=form, lang=lang, ui_text=ui_text)