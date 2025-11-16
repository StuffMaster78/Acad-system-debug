from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import Sum, Q, Count
from decimal import Decimal
from .models import ClientWallet, ClientWalletTransaction
from django import forms


class WalletAdjustmentForm(forms.Form):
    """Form for admin wallet adjustments"""
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text="Amount to adjust (positive for credit, negative for debit)"
    )
    reason = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Reason for this adjustment"
    )
    transaction_type = forms.ChoiceField(
        choices=[
            ('adjustment', 'Adjustment'),
            ('top-up', 'Top-Up'),
            ('refund', 'Refund'),
            ('bonus', 'Bonus'),
        ],
        initial='adjustment'
    )


@admin.register(ClientWallet)
class ClientWalletAdmin(admin.ModelAdmin):
    """Enhanced admin for ClientWallet with totals, filtering, and adjustment actions"""
    
    list_display = ['id', 'client_name', 'website', 'balance_display', 'currency', 'loyalty_points', 'adjust_wallet_link', 'last_updated']
    list_filter = ['website', 'currency', 'last_updated']
    search_fields = ['user__email', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['balance', 'last_updated', 'created_at', 'updated_at']
    ordering = ['-balance']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('user', 'website')
        }),
        ('Wallet Details', {
            'fields': ('balance', 'currency', 'loyalty_points', 'last_updated')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_name(self, obj):
        """Display client name with email"""
        if obj.user:
            name = f"{obj.user.get_full_name() or obj.user.username}"
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                name,
                obj.user.email
            )
        return "-"
    client_name.short_description = "Client"
    client_name.admin_order_field = 'user__email'
    
    def balance_display(self, obj):
        """Display balance with color coding"""
        if obj.balance >= Decimal('1000'):
            color = 'green'
        elif obj.balance >= Decimal('100'):
            color = 'blue'
        elif obj.balance > Decimal('0'):
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">${:,.2f}</span>',
            color,
            obj.balance
        )
    balance_display.short_description = "Balance"
    balance_display.admin_order_field = 'balance'
    
    def adjust_wallet_link(self, obj):
        """Link to adjust wallet"""
        url = f'/admin/client_wallet/clientwallet/{obj.id}/adjust/'
        return format_html(
            '<a href="{}" class="button" style="padding: 5px 10px; text-decoration: none; background: #417690; color: white; border-radius: 3px;">Adjust</a>',
            url
        )
    adjust_wallet_link.short_description = "Actions"
    adjust_wallet_link.allow_tags = True
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'website')
    
    def changelist_view(self, request, extra_context=None):
        """Add summary totals to the changelist"""
        extra_context = extra_context or {}
        
        # Get the base queryset
        qs = self.get_queryset(request)
        
        # Apply filters from request
        from django.contrib.admin.views.main import ChangeList
        cl = ChangeList(request, self.model, self.list_display, self.list_display_links,
                        self.list_filter, self.date_hierarchy, self.search_fields,
                        self.list_select_related, self.list_per_page, self.list_max_show_all,
                        self.list_editable, self)
        filtered_qs = cl.get_queryset(request)
        
        try:
            # Calculate totals for filtered results
            totals = filtered_qs.aggregate(
                total_balance=Sum('balance'),
                total_wallets=Count('id'),
                total_loyalty_points=Sum('loyalty_points')
            )
            
            # Group by website
            website_totals = filtered_qs.values('website__name', 'website__domain').annotate(
                total_balance=Sum('balance'),
                wallet_count=Count('id')
            ).order_by('-total_balance')
            
            extra_context['summary'] = {
                'total_balance': totals['total_balance'] or Decimal('0.00'),
                'total_wallets': totals['total_wallets'] or 0,
                'total_loyalty_points': totals['total_loyalty_points'] or 0,
                'website_totals': list(website_totals),
            }
                
        except Exception as e:
            # If there's an error, just continue without summary
            extra_context['summary'] = {
                'total_balance': Decimal('0.00'),
                'total_wallets': 0,
                'total_loyalty_points': 0,
                'website_totals': [],
            }
        
        # Get the response from parent
        response = super().changelist_view(request, extra_context)
        
        # Update response context if it's a TemplateResponse
        if hasattr(response, 'context_data'):
            response.context_data.update(extra_context)
        
        return response
    
    def get_urls(self):
        """Add custom URLs for wallet adjustments"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:wallet_id>/adjust/',
                self.admin_site.admin_view(self.adjust_wallet_view),
                name='client_wallet_adjust',
            ),
        ]
        return custom_urls + urls
    
    def adjust_wallet_view(self, request, wallet_id):
        """View for adjusting wallet balance"""
        wallet = ClientWallet.objects.select_related('user', 'website').get(id=wallet_id)
        
        if request.method == 'POST':
            form = WalletAdjustmentForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                reason = form.cleaned_data['reason']
                transaction_type = form.cleaned_data['transaction_type']
                
                try:
                    if amount > 0:
                        # Credit - use the wallet's credit method which creates transaction
                        wallet.credit_wallet(amount, reason)
                        # Update transaction type if different from default
                        if transaction_type != 'top-up':
                            last_transaction = ClientWalletTransaction.objects.filter(
                                wallet=wallet
                            ).order_by('-created_at').first()
                            if last_transaction:
                                last_transaction.transaction_type = transaction_type
                                last_transaction.save()
                        
                        messages.success(
                            request,
                            f'Successfully credited ${amount:,.2f} to {wallet.user.get_full_name() or wallet.user.username}\'s wallet.'
                        )
                    else:
                        # Debit (make amount positive)
                        debit_amount = abs(amount)
                        wallet.debit_wallet(debit_amount, reason)
                        # Update transaction type if different from default
                        if transaction_type != 'payment':
                            last_transaction = ClientWalletTransaction.objects.filter(
                                wallet=wallet
                            ).order_by('-created_at').first()
                            if last_transaction:
                                last_transaction.transaction_type = transaction_type
                                last_transaction.save()
                        
                        messages.success(
                            request,
                            f'Successfully debited ${debit_amount:,.2f} from {wallet.user.get_full_name() or wallet.user.username}\'s wallet.'
                        )
                    
                    return redirect('admin:client_wallet_clientwallet_changelist')
                    
                except ValueError as e:
                    messages.error(request, f'Error: {str(e)}')
                except Exception as e:
                    import traceback
                    messages.error(request, f'Unexpected error: {str(e)}')
                    # Log the full traceback for debugging
                    print(traceback.format_exc())
        else:
            form = WalletAdjustmentForm()
        
        context = {
            'title': f'Adjust Wallet: {wallet.user.get_full_name() or wallet.user.username}',
            'wallet': wallet,
            'form': form,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request, wallet),
            'has_change_permission': self.has_change_permission(request, wallet),
        }
        
        return render(request, 'admin/client_wallet/adjust_wallet.html', context)
    
    actions = ['credit_wallets', 'debit_wallets']
    
    def credit_wallets(self, request, queryset):
        """Bulk credit action"""
        # This would need a custom form, for now just show message
        messages.info(
            request,
            f'Selected {queryset.count()} wallets. Use individual wallet adjustment for credits.'
        )
    credit_wallets.short_description = "Credit selected wallets"
    
    def debit_wallets(self, request, queryset):
        """Bulk debit action"""
        messages.info(
            request,
            f'Selected {queryset.count()} wallets. Use individual wallet adjustment for debits.'
        )
    debit_wallets.short_description = "Debit selected wallets"


@admin.register(ClientWalletTransaction)
class ClientWalletTransactionAdmin(admin.ModelAdmin):
    """Admin for wallet transactions"""
    
    list_display = ['id', 'wallet_client', 'transaction_type', 'amount_display', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at', 'website']
    search_fields = ['wallet__user__email', 'wallet__user__username', 'description', 'reference_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def wallet_client(self, obj):
        """Display wallet client info"""
        if obj.wallet and obj.wallet.user:
            return format_html(
                '{}<br><small>{}</small>',
                obj.wallet.user.get_full_name() or obj.wallet.user.username,
                obj.wallet.user.email
            )
        return "-"
    wallet_client.short_description = "Client"
    
    def amount_display(self, obj):
        """Display amount with color"""
        color = 'green' if obj.amount > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">${:,.2f}</span>',
            color,
            abs(obj.amount)
        )
    amount_display.short_description = "Amount"
    amount_display.admin_order_field = 'amount'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('wallet__user', 'website')
