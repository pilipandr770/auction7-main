from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import current_user, login_required
from app import db
from .models import Proposal, Vote
from .forms import ProposalForm
from app.utils.dao_i18n import dao_ui
from app.utils.i18n_ui import ui_text
from app.models.token import Token

dao_bp = Blueprint('dao', __name__)

@dao_bp.route('/')
def index():
    lang = session.get('lang', 'ua')
    proposals = Proposal.query.order_by(Proposal.created_at.desc()).all()
    
    # Check if user has tokens for template rendering
    has_tokens = False
    if current_user.is_authenticated:
        tokens = Token.query.filter_by(user_id=current_user.id).first()
        has_tokens = tokens and tokens.amount > 0
    
    return render_template('dao/index.html', proposals=proposals, lang=lang, ui_text=ui_text, dao_ui=dao_ui, has_tokens=has_tokens)

@dao_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    lang = session.get('lang', 'ua')
    
    # Check if user has tokens
    tokens = Token.query.filter_by(user_id=current_user.id).first()
    if not tokens or tokens.amount == 0:
        flash_message = {
            'ua': 'Вам потрібно мати токени AUKTO щоб створювати пропозиції',
            'en': 'You need to have AUKTO tokens to create proposals',
            'de': 'Sie benötigen AUKTO-Token, um Vorschläge zu erstellen'
        }
        flash(flash_message.get(lang, flash_message['en']))
        return redirect(url_for('token.token_info'))
    
    form = ProposalForm()
    if form.validate_on_submit():
        proposal = Proposal(
            title=form.title.data, 
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(proposal)
        db.session.commit()
        return redirect(url_for('dao.index'))
    return render_template('dao/create.html', form=form, lang=lang, ui_text=ui_text, dao_ui=dao_ui)

@dao_bp.route('/proposal/<int:proposal_id>')
def view_proposal(proposal_id):
    lang = session.get('lang', 'ua')
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Check if user has tokens and has already voted
    has_tokens = False
    already_voted = False
    if current_user.is_authenticated:
        tokens = Token.query.filter_by(user_id=current_user.id).first()
        has_tokens = tokens and tokens.amount > 0
        
        # Check if user already voted
        if has_tokens:
            vote = Vote.query.filter_by(
                user_id=current_user.id,
                proposal_id=proposal_id
            ).first()
            already_voted = vote is not None
    
    return render_template('dao/proposal.html', 
                         proposal=proposal, 
                         lang=lang, 
                         ui_text=ui_text, 
                         dao_ui=dao_ui,
                         has_tokens=has_tokens,
                         already_voted=already_voted)

@dao_bp.route('/proposal/<int:proposal_id>/vote', methods=['POST'])
@login_required
def vote(proposal_id):
    lang = session.get('lang', 'ua')
    proposal = Proposal.query.get_or_404(proposal_id)
    vote_type = request.form.get('vote_type')
    
    # Check if user has tokens
    tokens = Token.query.filter_by(user_id=current_user.id).first()
    if not tokens or tokens.amount == 0:
        flash_message = {
            'ua': 'Вам потрібно мати токени AUKTO щоб голосувати',
            'en': 'You need to have AUKTO tokens to vote',
            'de': 'Sie benötigen AUKTO-Token, um abzustimmen'
        }
        flash(flash_message.get(lang, flash_message['en']))
        return redirect(url_for('token.token_info'))
    
    # Check if user already voted
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        proposal_id=proposal_id
    ).first()
    
    if existing_vote:
        flash_message = {
            'ua': 'Ви вже проголосували за цю пропозицію',
            'en': 'You have already voted on this proposal',
            'de': 'Sie haben bereits über diesen Vorschlag abgestimmt'
        }
        flash(flash_message.get(lang, flash_message['en']))
    else:
        if vote_type == 'for':
            proposal.votes_for += 1
            vote_record = Vote(user_id=current_user.id, proposal_id=proposal_id, vote_type='for')
        elif vote_type == 'against':
            proposal.votes_against += 1
            vote_record = Vote(user_id=current_user.id, proposal_id=proposal_id, vote_type='against')
        
        db.session.add(vote_record)
        db.session.commit()
    
    return redirect(url_for('dao.view_proposal', proposal_id=proposal_id))
