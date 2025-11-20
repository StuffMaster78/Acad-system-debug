"""
Wallet-related notification templates.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple
from notifications_system.templates.base import WalletNotificationTemplate
from notifications_system.registry.template_registry import register_template_class


@register_template_class("wallet.funded")
class WalletFundedTemplate(WalletNotificationTemplate):
    """Template for when a wallet is funded."""
    
    event_name = "wallet.funded"
    priority = 7
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render wallet funded notification."""
        user_ctx = self._get_user_context(context)
        wallet_ctx = self._get_wallet_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        
        title = f"Wallet Funded: {wallet_ctx['currency']} {wallet_ctx['transaction_amount']}"
        
        text = f"""Hello {user_ctx['username']},

Your wallet has been successfully funded.

Transaction Details:
- Amount: {wallet_ctx['currency']} {wallet_ctx['transaction_amount']}
- Transaction ID: {wallet_ctx['transaction_id']}
- New Balance: {wallet_ctx['currency']} {wallet_ctx['balance']}

You can now use your wallet balance to place orders or make payments.

View Wallet: {frontend_url}/wallet

Thank you for your deposit!

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Wallet Funded 💰</h2>
            <p>Hello {user_ctx['username']},</p>
            <p>Your wallet has been successfully funded.</p>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Transaction Details</h3>
                <ul style="list-style: none; padding: 0; color: #155724;">
                    <li><strong>Amount:</strong> {wallet_ctx['currency']} {wallet_ctx['transaction_amount']}</li>
                    <li><strong>Transaction ID:</strong> {wallet_ctx['transaction_id']}</li>
                    <li><strong>New Balance:</strong> {wallet_ctx['currency']} {wallet_ctx['balance']}</li>
                </ul>
            </div>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <p style="margin: 0; color: #004085;">
                    <strong>Next Steps:</strong> You can now use your wallet balance to place orders or make payments.
                </p>
            </div>
            
            <p>
                <a href="{frontend_url}/wallet" 
                   style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Wallet
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                Thank you for your deposit!<br>
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("wallet.balance_low")
class WalletBalanceLowTemplate(WalletNotificationTemplate):
    """Template for low wallet balance warnings."""
    
    event_name = "wallet.balance_low"
    priority = 6
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render low balance warning notification."""
        user_ctx = self._get_user_context(context)
        wallet_ctx = self._get_wallet_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        threshold = context.get("threshold", 10)
        
        title = f"Low Wallet Balance Warning"
        
        text = f"""Hello {user_ctx['username']},

Your wallet balance is running low.

Current Balance: {wallet_ctx['currency']} {wallet_ctx['balance']}
Warning Threshold: {wallet_ctx['currency']} {threshold}

To avoid any interruptions to your orders, please consider adding funds to your wallet.

Add Funds: {frontend_url}/wallet/add-funds

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #ffc107;">Low Wallet Balance Warning ⚠️</h2>
            <p>Hello {user_ctx['username']},</p>
            <p>Your wallet balance is running low.</p>
            
            <div style="background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3 style="margin-top: 0; color: #856404;">Balance Information</h3>
                <ul style="list-style: none; padding: 0; color: #856404;">
                    <li><strong>Current Balance:</strong> {wallet_ctx['currency']} {wallet_ctx['balance']}</li>
                    <li><strong>Warning Threshold:</strong> {wallet_ctx['currency']} {threshold}</li>
                </ul>
            </div>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <p style="margin: 0; color: #004085;">
                    <strong>Recommendation:</strong> To avoid any interruptions to your orders, please consider adding funds to your wallet.
                </p>
            </div>
            
            <p>
                <a href="{frontend_url}/wallet/add-funds" 
                   style="background: #ffc107; color: #212529; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Add Funds
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("wallet.balance_critical")
class WalletBalanceCriticalTemplate(WalletNotificationTemplate):
    """Template for critical wallet balance warnings."""
    
    event_name = "wallet.balance_critical"
    priority = 9
    channels = ["email", "in_app", "sms"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render critical balance warning notification."""
        user_ctx = self._get_user_context(context)
        wallet_ctx = self._get_wallet_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        threshold = context.get("threshold", 5)
        
        title = f"CRITICAL: Wallet Balance Very Low"
        
        text = f"""URGENT: {user_ctx['username']},

Your wallet balance is critically low and may affect your active orders.

Current Balance: {wallet_ctx['currency']} {wallet_ctx['balance']}
Critical Threshold: {wallet_ctx['currency']} {threshold}

IMMEDIATE ACTION REQUIRED:
- Add funds to your wallet immediately
- Check your active orders for potential issues
- Contact support if you need assistance

Add Funds Now: {frontend_url}/wallet/add-funds
Contact Support: {frontend_url}/support

This is an automated critical alert.

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc3545;">CRITICAL: Wallet Balance Very Low 🚨</h2>
            <p><strong>URGENT:</strong> {user_ctx['username']},</p>
            <p>Your wallet balance is critically low and may affect your active orders.</p>
            
            <div style="background: #f8d7da; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <h3 style="margin-top: 0; color: #721c24;">Critical Balance Information</h3>
                <ul style="list-style: none; padding: 0; color: #721c24;">
                    <li><strong>Current Balance:</strong> {wallet_ctx['currency']} {wallet_ctx['balance']}</li>
                    <li><strong>Critical Threshold:</strong> {wallet_ctx['currency']} {threshold}</li>
                </ul>
            </div>
            
            <div style="background: #dc3545; color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: white;">IMMEDIATE ACTION REQUIRED:</h3>
                <ul style="color: white;">
                    <li>Add funds to your wallet immediately</li>
                    <li>Check your active orders for potential issues</li>
                    <li>Contact support if you need assistance</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{frontend_url}/wallet/add-funds" 
                   style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-right: 10px;">
                    Add Funds Now
                </a>
                <a href="{frontend_url}/support" 
                   style="background: #6c757d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Contact Support
                </a>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; text-align: center;">
                This is an automated critical alert.<br>
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("wallet.withdrawal_approved")
class WalletWithdrawalApprovedTemplate(WalletNotificationTemplate):
    """Template for approved withdrawal notifications."""
    
    event_name = "wallet.withdrawal_approved"
    priority = 7
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render withdrawal approved notification."""
        user_ctx = self._get_user_context(context)
        wallet_ctx = self._get_wallet_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        withdrawal = context.get("withdrawal", {})
        
        title = f"Withdrawal Approved: {wallet_ctx['currency']} {wallet_ctx['transaction_amount']}"
        
        text = f"""Hello {user_ctx['username']},

Your withdrawal request has been approved.

Withdrawal Details:
- Amount: {wallet_ctx['currency']} {wallet_ctx['transaction_amount']}
- Transaction ID: {wallet_ctx['transaction_id']}
- Withdrawal ID: {withdrawal.get('id', 'N/A')}
- Processing Time: {withdrawal.get('processing_time', '1-3 business days')}

The funds will be transferred to your registered payment method within the specified processing time.

View Transaction: {frontend_url}/wallet/transactions/{wallet_ctx['transaction_id']}

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Withdrawal Approved ✅</h2>
            <p>Hello {user_ctx['username']},</p>
            <p>Your withdrawal request has been approved.</p>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Withdrawal Details</h3>
                <ul style="list-style: none; padding: 0; color: #155724;">
                    <li><strong>Amount:</strong> {wallet_ctx['currency']} {wallet_ctx['transaction_amount']}</li>
                    <li><strong>Transaction ID:</strong> {wallet_ctx['transaction_id']}</li>
                    <li><strong>Withdrawal ID:</strong> {withdrawal.get('id', 'N/A')}</li>
                    <li><strong>Processing Time:</strong> {withdrawal.get('processing_time', '1-3 business days')}</li>
                </ul>
            </div>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <p style="margin: 0; color: #004085;">
                    <strong>Next Steps:</strong> The funds will be transferred to your registered payment method within the specified processing time.
                </p>
            </div>
            
            <p>
                <a href="{frontend_url}/wallet/transactions/{wallet_ctx['transaction_id']}" 
                   style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Transaction
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html
