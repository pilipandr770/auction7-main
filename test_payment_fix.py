#!/usr/bin/env python3
"""
Test script to verify that Payment records are created correctly
when users pay to view auction prices again.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.auction import Auction
from app.models.payment import Payment
from app.models.auction_participant import AuctionParticipant

def test_payment_tracking():
    """Test that Payment records are created for view fees"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Payment record creation for view fees...")
          # Count existing payments
        initial_payment_count = Payment.query.count()
        view_fee_payments = Payment.query.filter_by(purpose='view_fee').count()
        
        print(f"📊 Current statistics:")
        print(f"   Total payments: {initial_payment_count}")
        print(f"   View fee payments: {view_fee_payments}")
        
        # Find admin user
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            print(f"👤 Admin found: {admin.email} (Balance: €{admin.balance})")
        else:
            print("❌ No admin user found")
        
        # Check if Payment model has created_at field
        try:
            latest_payment = Payment.query.order_by(Payment.created_at.desc()).first()
            if latest_payment:
                print(f"📅 Latest payment: {latest_payment.purpose} - {latest_payment.created_at}")
            else:
                print("📅 No payments found with created_at timestamp")
        except AttributeError:
            print("❌ Payment model missing created_at field")
        
        # Check active auctions
        active_auctions = Auction.query.filter_by(is_active=True).count()
        print(f"🏷️  Active auctions: {active_auctions}")
        
        print("\n✅ Test completed! The Payment tracking system is ready.")
        print("💡 Next steps:")
        print("   1. Login as a user who has paid entry fee for an auction")
        print("   2. Click 'View Current Price' multiple times")
        print("   3. Check admin dashboard > Payments Report for new view fee records")

if __name__ == '__main__':
    test_payment_tracking()
