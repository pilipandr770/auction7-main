from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify  # add request, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.auction import Auction
from app.models.payment import Payment  # add Payment import
from app.models.auction_participant import AuctionParticipant  # add AuctionParticipant import
from app import db  # add db import
from app.utils.i18n_messages import get_message
from app.utils.i18n_ui import ui_text
from flask import session
from sqlalchemy import func, and_  # add sqlalchemy imports
from datetime import datetime, timedelta  # add datetime imports

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

    # Статистика доходів від просмотрів за останній місяць
    one_month_ago = datetime.now() - timedelta(days=30)
    view_payments = Payment.query.filter(
        Payment.purpose == 'view_fee',
        Payment.created_at >= one_month_ago if hasattr(Payment, 'created_at') else True
    ).all()
    
    total_view_revenue = sum(payment.amount for payment in view_payments)
    view_count = len(view_payments)

    # Статистика по активним аукціонам
    active_auctions = Auction.query.filter_by(is_active=True).count()
    closed_auctions = Auction.query.filter_by(is_active=False).count()
    
    # Топ пользователи по тратам
    top_spenders = db.session.query(
        User.username, 
        User.email,
        func.sum(Payment.amount).label('total_spent')
    ).join(Payment, User.id == Payment.user_id)\
     .group_by(User.id)\
     .order_by(func.sum(Payment.amount).desc())\
     .limit(5).all()

    # Статистика по участию в аукціонах
    total_participants = AuctionParticipant.query.count()
    paid_participants = AuctionParticipant.query.filter_by(has_paid_entry=True).count()

    # Відображення панелі адміністратора
    return render_template('admin/dashboard.html', 
                           users=users, 
                           auctions=auctions, 
                           admin_balance=admin_balance,
                           total_view_revenue=total_view_revenue,
                           view_count=view_count,
                           active_auctions=active_auctions,
                           closed_auctions=closed_auctions,
                           top_spenders=top_spenders,
                           total_participants=total_participants,
                           paid_participants=paid_participants,
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


@admin_bp.route('/user_management', methods=['GET'])
@login_required 
def user_management():
    if not current_user.is_admin:
        return "Доступ заборонено", 403
        
    users = User.query.all()
    return render_template('admin/user_management.html', 
                         users=users,
                         lang=session.get('lang', 'ua'), 
                         ui_text=ui_text)

@admin_bp.route('/manage_user/<int:user_id>', methods=['POST'])
@login_required
def manage_user(user_id):
    if not current_user.is_admin:
        return jsonify({"error": "Доступ заборонено"}), 403
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Користувача не знайдено"}), 404
        
    action = request.json.get('action')
    
    try:
        if action == 'add_balance':
            amount = float(request.json.get('amount', 0))
            user.add_balance(amount)
            return jsonify({"message": f"Баланс користувача поповнено на {amount} EUR"})
            
        elif action == 'deduct_balance':
            amount = float(request.json.get('amount', 0))
            if user.can_afford(amount):
                user.deduct_balance(amount)
                return jsonify({"message": f"З балансу користувача списано {amount} EUR"})
            else:
                return jsonify({"error": "Недостатньо коштів"}), 400
                
        elif action == 'toggle_admin':
            user.is_admin = not user.is_admin
            db.session.commit()
            status = "адміністратором" if user.is_admin else "звичайним користувачем"
            return jsonify({"message": f"Користувач тепер є {status}"})
            
        elif action == 'toggle_verified':
            user.is_verified = not user.is_verified
            db.session.commit()
            status = "верифіковано" if user.is_verified else "не верифіковано"
            return jsonify({"message": f"Користувача {status}"})
            
        else:
            return jsonify({"error": "Невідома дія"}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Помилка: {str(e)}"}), 500

@admin_bp.route('/payments_report', methods=['GET'])
@login_required
def payments_report():
    if not current_user.is_admin:
        return "Доступ заборонено", 403
    
    # Отримання всіх платежів з деталями
    payments = db.session.query(
        Payment,
        User.username,
        User.email,
        Auction.title
    ).join(User, Payment.user_id == User.id)\
     .join(Auction, Payment.auction_id == Auction.id)\
     .order_by(Payment.id.desc())\
     .limit(100).all()
    
    # Групування за призначенням
    entry_payments = [p for p in payments if p[0].purpose == 'entry_fee']
    view_payments = [p for p in payments if p[0].purpose == 'view_fee']
    
    return render_template('admin/payments_report.html',
                         payments=payments,
                         entry_payments=entry_payments,
                         view_payments=view_payments,
                         lang=session.get('lang', 'ua'),
                         ui_text=ui_text)

@admin_bp.route('/auction_management', methods=['GET'])
@login_required
def auction_management():
    if not current_user.is_admin:
        return "Доступ заборонено", 403
    
    auctions = db.session.query(
        Auction,
        User.username.label('seller_name'),
        func.count(AuctionParticipant.id).label('participant_count')
    ).join(User, Auction.seller_id == User.id)\
     .outerjoin(AuctionParticipant, Auction.id == AuctionParticipant.auction_id)\
     .group_by(Auction.id)\
     .order_by(Auction.id.desc()).all()
    
    return render_template('admin/auction_management.html',
                         auctions=auctions,
                         lang=session.get('lang', 'ua'),
                         ui_text=ui_text)

@admin_bp.route('/manage_auction/<int:auction_id>', methods=['POST'])
@login_required
def manage_auction(auction_id):
    if not current_user.is_admin:
        return jsonify({"error": "Доступ заборонено"}), 403
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({"error": "Аукціон не знайдено"}), 404
    
    action = request.json.get('action')
    
    try:
        if action == 'force_close':
            auction.is_active = False
            db.session.commit()
            return jsonify({"message": "Аукціон примусово закрито"})
            
        elif action == 'reopen':
            auction.is_active = True
            db.session.commit()
            return jsonify({"message": "Аукціон відновлено"})
            
        elif action == 'delete':
            # Видаляємо учасників аукціону
            AuctionParticipant.query.filter_by(auction_id=auction_id).delete()
            # Видаляємо платежі
            Payment.query.filter_by(auction_id=auction_id).delete()
            # Видаляємо аукціон
            db.session.delete(auction)
            db.session.commit()
            return jsonify({"message": "Аукціон видалено"})
            
        else:
            return jsonify({"error": "Невідома дія"}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Помилка: {str(e)}"}), 500
