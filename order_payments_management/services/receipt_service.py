"""
Service for generating payment receipts as PDFs.
"""
from io import BytesIO
from decimal import Decimal
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReceiptService:
    """Service for generating payment receipts."""
    
    @staticmethod
    def generate_receipt_pdf(transaction_data: Dict[str, Any], website_name: str = "Writing System") -> BytesIO:
        """
        Generate a PDF receipt for a payment transaction.
        
        Args:
            transaction_data: Dictionary containing transaction information
            website_name: Name of the website/company
            
        Returns:
            BytesIO object containing the PDF
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install it with: pip install reportlab"
            )
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        
        # Header
        elements.append(Paragraph(f"<b>{website_name}</b>", title_style))
        elements.append(Paragraph("Payment Receipt", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Receipt Details Table
        receipt_data = [
            ['Receipt Number:', transaction_data.get('reference_id', transaction_data.get('transaction_id', 'N/A'))],
            ['Date:', transaction_data.get('created_at', timezone.now()).strftime('%B %d, %Y %I:%M %p') if hasattr(transaction_data.get('created_at'), 'strftime') else str(transaction_data.get('created_at', 'N/A'))],
            ['Transaction ID:', transaction_data.get('transaction_id', 'N/A')],
        ]
        
        # Add order ID if available
        if transaction_data.get('order_id'):
            receipt_data.append(['Order ID:', str(transaction_data['order_id'])])
        
        # Payment Details
        elements.append(Paragraph("<b>Payment Details</b>", heading_style))
        receipt_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
        receipt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(receipt_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Payment Information
        elements.append(Paragraph("<b>Payment Information</b>", heading_style))
        payment_type = transaction_data.get('payment_type', transaction_data.get('type', 'N/A'))
        payment_type_label = ReceiptService._format_payment_type(payment_type)
        
        payment_data = [
            ['Payment Type:', payment_type_label],
            ['Payment Method:', transaction_data.get('payment_method', 'N/A')],
            ['Status:', transaction_data.get('status', 'N/A').title()],
            ['Amount:', f"${transaction_data.get('amount', 0):,.2f}"],
        ]
        
        payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Customer Information
        if transaction_data.get('client'):
            elements.append(Paragraph("<b>Customer Information</b>", heading_style))
            client = transaction_data['client']
            client_data = [
                ['Customer ID:', str(client.get('id', 'N/A'))],
                ['Email:', client.get('email', 'N/A')],
            ]
            if client.get('username'):
                client_data.append(['Username:', client.get('username', 'N/A')])
            
            client_table = Table(client_data, colWidths=[2*inch, 4*inch])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(client_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            "<i>This is an official receipt for your records. Please keep this document for your records.</i>",
            ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=1)
        ))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def _format_payment_type(payment_type: str) -> str:
        """Format payment type for display."""
        type_mapping = {
            'order_payment': 'Order Payment',
            'standard': 'Standard Order Payment',
            'predefined_special': 'Special Order Payment',
            'estimated_special': 'Estimated Special Order Payment',
            'special_installment': 'Special Order Installment',
            'class_payment': 'Class Payment',
            'wallet_transaction': 'Wallet Transaction',
            'client_wallet': 'Wallet Transaction',
            'writer_wallet': 'Writer Payment',
            'writer_payment': 'Writer Payment',
        }
        return type_mapping.get(payment_type, payment_type.replace('_', ' ').title())
    
    @staticmethod
    def create_pdf_response(pdf_buffer: BytesIO, filename: str) -> HttpResponse:
        """
        Create an HttpResponse with PDF content.
        
        Args:
            pdf_buffer: BytesIO buffer containing PDF
            filename: Name for the downloaded file
            
        Returns:
            HttpResponse with PDF content
        """
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

