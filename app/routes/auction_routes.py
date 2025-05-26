from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.auction import Auction
from app.models.user import User
from app.models.auction_participant import AuctionParticipant
from app.models.payment import Payment
from blockchain_payments.payment_token_discount import get_user_discount
from app.utils.i18n_messages import get_message
from app.utils.i18n_ui import ui_text

auction_bp = Blueprint('auction', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('app', 'static', 'images', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ======================= CREATE AUCTION =======================

@auction_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_auction():
    lang = session.get('lang', 'ua')
    if request.method == 'POST':
        if current_user.user_type != 'seller':
            flash(get_message("only_sellers_create", lang), "error")
            return redirect(url_for('user.seller_dashboard', email=current_user.email))

        title = request.form.get('title')
        description = request.form.get('description')
        starting_price = request.form.get('starting_price')

        if not title or not description or not starting_price:
            flash(get_message("all_fields_required", lang), "error")
            return redirect(url_for('user.seller_dashboard', email=current_user.email))

        try:
            starting_price = float(starting_price)
        except ValueError:
            flash(get_message("price_must_be_number", lang), "error")
            return redirect(url_for('user.seller_dashboard', email=current_user.email))

        photos = []
        main_photo_idx = int(request.form.get('main_photo_idx', 0))
        if 'photos' in request.files:
            files = request.files.getlist('photos')
            if len(files) > 10:
                flash(get_message("max_10_photos", lang), "error")
                return redirect(url_for('user.seller_dashboard', email=current_user.email))
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    photos.append(f"images/uploads/{filename}")

        try:
            new_auction = Auction(
                title=title,
                description=description,
                starting_price=starting_price,
                seller_id=current_user.id,
                photos=photos,
                main_photo_idx=main_photo_idx if 0 <= main_photo_idx < len(photos) else 0
            )
            db.session.add(new_auction)
            db.session.commit()
            flash(get_message('auction_action_success', lang), 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Помилка створення аукціону: {e}")
            flash(get_message('auction_action_error', lang), 'error')

        return redirect(url_for('user.seller_dashboard', email=current_user.email))

    # GET-запит (форма створення)
    if lang == 'en':
        return render_template('auctions/create_auction_en.html', lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('auctions/create_auction_de.html', lang=lang, ui_text=ui_text)
    return render_template('auctions/create_auction.html', lang=lang, ui_text=ui_text)

# ======================= AUCTION LIST =======================

@auction_bp.route('/list', methods=['GET'])
def auction_list():
    lang = session.get('lang', 'ua')
    auctions = Auction.query.filter_by(is_active=True).all()
    if lang == 'en':
        return render_template('auctions/auction_list_en.html', auctions=auctions, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('auctions/auction_list_de.html', auctions=auctions, lang=lang, ui_text=ui_text)
    return render_template('auctions/auction_list.html', auctions=auctions, lang=lang, ui_text=ui_text)

# ======================= AUCTION DETAIL =======================

@auction_bp.route('/<int:auction_id>', methods=['GET', 'POST'])
def auction_detail(auction_id):
    lang = session.get('lang', 'ua')
    try:
        auction = Auction.query.get_or_404(auction_id)
    except Exception as e:
        print(f"Error fetching auction with ID {auction_id}: {e}")
        flash(get_message('auction_not_found', lang), 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({"error": get_message('login_required', lang)}), 401

        try:
            entry_price = auction.starting_price * 0.01
            participant = AuctionParticipant.query.filter_by(auction_id=auction_id, user_id=current_user.id).first()

            if participant and participant.has_paid_entry:
                return jsonify({"error": get_message('already_participating', lang)}), 400

            if current_user.balance < entry_price:
                return jsonify({"error": get_message('insufficient_funds', lang)}), 400

            buyer = User.query.get(current_user.id)
            buyer.deduct_balance(entry_price)

            auction.total_participants += 1
            auction.current_price -= entry_price

            if auction.current_price <= 0:
                auction.current_price = 0
                auction.is_active = False

            if not participant:
                participant = AuctionParticipant(auction_id=auction_id, user_id=current_user.id)
                db.session.add(participant)

            participant.mark_paid_entry()
            db.session.commit()

            return jsonify({
                "message": get_message('participation_success', lang),
                "participants": auction.total_participants,
                "final_price": auction.current_price
            }), 200

        except Exception as e:
            db.session.rollback()
            print(f"Помилка участі в аукціоні: {e}")
            return jsonify({"error": get_message('participation_error', lang)}), 500

    if lang == 'en':
        return render_template('auctions/auction_detail_en.html', auction=auction, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('auctions/auction_detail_de.html', auction=auction, lang=lang, ui_text=ui_text)
    return render_template('auctions/auction_detail.html', auction=auction, lang=lang, ui_text=ui_text)

# ======================= AUCTION CLOSE =======================

@auction_bp.route('/close/<int:auction_id>', methods=['POST', 'GET'])
@login_required
def close_auction(auction_id):
    lang = session.get('lang', 'ua')
    auction = Auction.query.get(auction_id)
    if not auction:
        flash(get_message('auction_not_found', lang), 'error')
        return redirect(url_for('main.index'))

    if not auction.is_active:
        flash(get_message('auction_already_closed', lang), 'info')
        return redirect(url_for('main.index'))

    participant = AuctionParticipant.query.filter_by(auction_id=auction_id, user_id=current_user.id).first()
    if not participant or not participant.has_paid_entry:
        flash(get_message('participation_required_for_close', lang), 'error')
        return redirect(url_for('main.index'))    if current_user.balance < auction.current_price:
        flash(get_message('insufficient_funds', lang), 'error')
        return redirect(url_for('main.index'))
    
    try:
        current_user.deduct_balance(auction.current_price)
        seller = User.query.get(auction.seller_id)
        total_entry = auction.total_participants * auction.starting_price * 0.01
        total_revenue = total_entry + auction.current_price
        seller.add_balance(total_revenue)

        auction.is_active = False
        auction.winner_id = current_user.id
        auction.total_earnings = total_revenue
        db.session.commit()

        flash(get_message('auction_closed_success', lang), 'success')
        # Після закриття показуємо сторінку завершення з даними продавця
        if lang == 'en':
            return render_template('auctions/auction_close_en.html', auction=auction, seller=seller, lang=lang, ui_text=ui_text)
        elif lang == 'de':
            return render_template('auctions/auction_close_de.html', auction=auction, seller=seller, lang=lang, ui_text=ui_text)
        return render_template('auctions/auction_close.html', auction=auction, seller=seller, lang=lang, ui_text=ui_text)

    except Exception as e:
        db.session.rollback()
        print(f"Error closing auction: {e}")
        flash(get_message('auction_close_failed', lang), 'error')
        return redirect(url_for('main.index'))

# ======================= VIEW AUCTION PRICE =======================

@auction_bp.route('/view/<int:auction_id>', methods=['POST'])
def view_auction_price(auction_id):
    lang = session.get('lang', 'ua')
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({"error": get_message('auction_not_found', lang)}), 404
    if not auction.is_active:
        return jsonify({"error": get_message('auction_closed', lang)}), 400

    if not current_user.is_authenticated:
        return jsonify({"error": get_message('login_required', lang)}), 401

    participant = AuctionParticipant.query.filter_by(auction_id=auction_id, user_id=current_user.id).first()
    if not participant or not participant.has_paid_entry:
        return jsonify({"error": get_message('not_participant', lang)}), 400

    try:
        view_price = 1.0  # Євро
        discount = 0
        if current_user.wallet_address:
            try:
                discount = get_user_discount(current_user.wallet_address)
            except Exception as e:
                print(f"[WARN] Не вдалося отримати знижку: {e}")

        final_price = round(view_price * (1 - discount / 100), 2)

        if not current_user.can_afford(final_price):
            return jsonify({"error": get_message('insufficient_funds', lang)}), 400

        current_user.deduct_balance(final_price)

        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            admin.add_balance(final_price)

        db.session.commit()

        return jsonify({
            "message": get_message('view_updated', lang),
            "discount_percent": discount,
            "view_price": final_price,
            "current_price": auction.current_price,
            "participants": auction.total_participants
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] view_auction_price: {e}")
        return jsonify({"error": get_message('view_update_error', lang)}), 500

@auction_bp.route('/contact_details/<int:auction_id>', methods=['GET'])
@login_required
def auction_contact_details(auction_id):
    lang = session.get('lang', 'ua')
    auction = Auction.query.get(auction_id)
    if not auction:
        flash(get_message('auction_not_found', lang), 'error')
        return redirect(url_for('main.index'))

    if not auction.winner_id or auction.is_active:
        flash(get_message('auction_not_closed', lang), 'error')
        return redirect(url_for('main.index'))

    # Покупець — показуємо контакти продавця
    if current_user.id == auction.winner_id:
        seller = User.query.get(auction.seller_id)
        if lang == 'en':
            return render_template('users/seller_contact_en.html', seller=seller, lang=lang, ui_text=ui_text)
        elif lang == 'de':
            return render_template('users/seller_contact_de.html', seller=seller, lang=lang, ui_text=ui_text)
        return render_template('users/seller_contact.html', seller=seller, lang=lang, ui_text=ui_text)

    # Продавець — показуємо контакти покупця (треба створити buyer_contact.html)
    if current_user.id == auction.seller_id:
        buyer = User.query.get(auction.winner_id)
        if lang == 'en':
            return render_template('users/buyer_contact_en.html', buyer=buyer, lang=lang, ui_text=ui_text)
        elif lang == 'de':
            return render_template('users/buyer_contact_de.html', buyer=buyer, lang=lang, ui_text=ui_text)
        return render_template('users/buyer_contact.html', buyer=buyer, lang=lang, ui_text=ui_text)

    # За замовчуванням повертаємо сторінку закриття
    if lang == 'en':
        return render_template('auctions/auction_close_en.html', auction=auction, lang=lang, ui_text=ui_text)
    elif lang == 'de':
        return render_template('auctions/auction_close_de.html', auction=auction, lang=lang, ui_text=ui_text)
    return render_template('auctions/auction_close.html', auction=auction, lang=lang, ui_text=ui_text)


@auction_bp.route('/view-price/<int:auction_id>', methods=['POST'])
@login_required
def view_price_again(auction_id):
    lang = session.get('lang', 'ua')
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({"error": get_message('auction_not_found', lang)}), 404
    if not auction.is_active:
        return jsonify({"error": get_message('auction_closed', lang)}), 400

    participant = AuctionParticipant.query.filter_by(auction_id=auction_id, user_id=current_user.id).first()
    if not participant or not participant.has_paid_entry:
        return jsonify({"error": get_message('not_participant', lang)}), 400

    try:
        view_price = 1.0  # Євро
        discount = 0
        if current_user.wallet_address:
            try:
                discount = get_user_discount(current_user.wallet_address)
            except Exception as e:
                print(f"[WARN] Не вдалося отримати знижку: {e}")

        final_price = round(view_price * (1 - discount / 100), 2)

        if not current_user.can_afford(final_price):
            return jsonify({"error": get_message('insufficient_funds', lang)}), 400

        current_user.deduct_balance(final_price)
        
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            admin.add_balance(final_price)
        
        # Create Payment record for view fee tracking
        payment = Payment(
            user_id=current_user.id,
            auction_id=auction_id,
            amount=final_price,
            purpose='view_fee',
            recipient='platform'
        )
        db.session.add(payment)

        db.session.commit()

        return jsonify({
            "message": get_message('view_updated', lang),
            "discount_percent": discount,
            "view_price": final_price,
            "current_price": auction.current_price,
            "participants": auction.total_participants
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] view_price_again: {e}")
        return jsonify({"error": get_message('view_update_error', lang)}), 500

# ======================= CONFIRM RECEIVED =======================

@auction_bp.route('/confirm-received/<int:auction_id>', methods=['POST'])
@login_required
def confirm_received(auction_id):
    lang = session.get('lang', 'ua')
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({"error": get_message('auction_not_found', lang)}), 404
    
    if auction.is_active:
        return jsonify({"error": "Аукціон ще активний"}), 400
        
    if current_user.id != auction.winner_id:
        return jsonify({"error": "Тільки переможець може підтвердити отримання"}), 403
        
    if auction.is_confirmed:
        return jsonify({"error": "Отримання вже підтверджено"}), 400
    
    try:
        auction.is_confirmed = True
        db.session.commit()
        return jsonify({"message": "Отримання товару підтверджено!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error confirming receipt: {e}")
        return jsonify({"error": "Помилка підтвердження"}), 500
