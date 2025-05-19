from flask import Blueprint, render_template, flash, redirect, url_for  # add flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User
from app.models.auction import Auction
from app import db  # add db import
from app.utils.i18n_messages import get_message
from app.utils.i18n_ui import ui_text
from flask import session

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    # Перевірка, чи є користувач адміністратором
    if not current_user.is_admin:
        return "Доступ заборонено", 403

    # Отримання списку користувачів та аукціонів
    users = User.query.all()
    auctions = Auction.query.all()

    # Розрахунок загального балансу адміністратора
    admin_balance = current_user.balance  # Поточний баланс адміністратора

    # Відображення панелі адміністратора
    return render_template('admin/dashboard.html', 
                           users=users, 
                           auctions=auctions, 
                           admin_balance=admin_balance,
                           lang=session.get('lang', 'ua'),
                           ui_text=ui_text)


@admin_bp.route('/verify_sellers', methods=['GET', 'POST'])
@login_required
def verify_sellers():
    if not current_user.is_admin:
        return "Доступ заборонено", 403

    unverified_sellers = User.query.filter_by(user_type='seller', is_verified=False).all()

    return render_template('admin/verify_sellers.html', sellers=unverified_sellers, lang=session.get('lang', 'ua'), ui_text=ui_text)



@admin_bp.route('/verify_seller/<int:user_id>', methods=['POST'])
@login_required
def verify_seller_action(user_id):
    if not current_user.is_admin:
        return "Доступ заборонено", 403

    seller = User.query.get(user_id)
    if not seller or seller.user_type != 'seller':
        flash("Продавця не знайдено", "error")
        return redirect(url_for('admin.verify_sellers'))

    lang = session.get('lang', 'ua')  # Отримання мови з сесії, за замовчуванням 'ua'
    try:
        seller.is_verified = True
        db.session.commit()
        flash(get_message('admin_action_success', lang), 'success')
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Seller verification failed: {e}")
        flash(get_message('admin_action_error', lang), 'error')
    return redirect(url_for('admin.verify_sellers'))
