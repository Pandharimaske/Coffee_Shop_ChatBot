import smtplib
import logging
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from src.config import settings
from src.graph.state import ProductItem

logger = logging.getLogger(__name__)

# ── HTML Template ───────────────────────────────────────────────────────────

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f9f6f2;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }}
        .header {{
            background: linear-gradient(135deg, #4b2c20 0%, #6f4e37 100%);
            color: #ffffff;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            letter-spacing: 1px;
        }}
        .content {{
            padding: 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #4b2c20;
            margin-bottom: 20px;
        }}
        .order-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .order-table th {{
            text-align: left;
            border-bottom: 2px solid #f0e6dc;
            padding: 10px;
            color: #8d6e63;
            font-size: 11px;
            text-transform: uppercase;
        }}
        .order-table td {{
            padding: 12px 10px;
            border-bottom: 1px solid #f0e6dc;
            vertical-align: middle;
        }}
        .product-img {{
            width: 50px;
            height: 50px;
            object-fit: cover;
            border-radius: 8px;
            background-color: #f0e6dc;
        }}
        .total-row td {{
            font-weight: bold;
            font-size: 18px;
            color: #4b2c20;
            border-bottom: none;
            padding-top: 25px;
        }}
        .footer {{
            background-color: #f0e6dc;
            padding: 20px;
            text-align: center;
            font-size: 14px;
            color: #8d6e63;
        }}
        .order-id {{
            color: #a1887f;
            font-size: 11px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Coffee Shop</h1>
            <p>Your receipt is here!</p>
        </div>
        <div class="content">
            <p class="greeting">Hey there! ☕</p>
            <p>Thank you for choosing us. We're currently preparing your delicious order with love. Here's a summary of what's coming your way:</p>
            
            <table class="order-table">
                <thead>
                    <tr>
                        <th style="width: 60px;"></th>
                        <th>Item</th>
                        <th>Unit</th>
                        <th>Qty</th>
                        <th style="text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows}
                    <tr class="total-row">
                        <td colspan="4" style="text-align: right;">Total Paid</td>
                        <td style="text-align: right;">₹{total:.2f}</td>
                    </tr>
                </tbody>
            </table>

            <p style="margin-top: 30px;">Enjoy your coffee! If you need anything else, just reply to your chat, and I'll be there to help.</p>
        </div>
        <div class="footer">
            <p>Brewed with perfection at Coffee Shop</p>
            <p class="order-id">Order ID: {order_id}</p>
        </div>
    </div>
</body>
</html>
"""

# ── Helper ──────────────────────────────────────────────────────────────────

def _format_items(items: List[ProductItem]) -> str:
    rows = []
    base_url = settings.app_url.rstrip("/")
    for item in items:
        # Determine image URL
        img_src = ""
        if item.image_url:
            if item.image_url.startswith("http"):
                img_src = item.image_url
            else:
                img_src = f"{base_url}/{item.image_url.lstrip('/')}"
        
        # Fallback image if none provided
        img_html = f'<img src="{img_src}" class="product-img" alt="{item.name}">' if img_src else '<div class="product-img" style="display: flex; align-items: center; justify-content: center; font-size: 20px;">☕</div>'

        rows.append(f"""
            <tr>
                <td>{img_html}</td>
                <td style="font-weight: 500;">{item.name}</td>
                <td style="color: #8d6e63; font-size: 13px;">₹{item.per_unit_price or 0:.2f}</td>
                <td>{item.quantity}</td>
                <td style="text-align: right; font-weight: 600;">₹{item.total_price or 0:.2f}</td>
            </tr>
        """)
    return "\n".join(rows)

# ── Core Logic ──────────────────────────────────────────────────────────────

async def send_order_receipt(recipient_email: str, items: List[ProductItem], total: float, order_id: str = "N/A"):
    """Sends a beautiful HTML receipt email in the background."""
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning(f"Skipping email for {recipient_email}: SMTP credentials not configured.")
        return

    try:
        # Generate HTML content
        item_rows = _format_items(items)
        html_content = EMAIL_TEMPLATE.format(
            item_rows=item_rows,
            total=total,
            order_id=order_id
        )

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "☕ Your Delicious Coffee Shop Receipt"
        message["From"] = settings.smtp_from_email
        message["To"] = recipient_email
        message.attach(MIMEText(html_content, "html"))

        # Send email (using asyncio.to_thread to prevent blocking)
        await asyncio.to_thread(_send_sync, recipient_email, message)
        logger.info(f"Receipt email successfully sent to {recipient_email}")

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}", exc_info=True)


def _send_sync(recipient: str, message: MIMEMultipart):
    """Synchronous smtp sending logic to be run in a thread."""
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password.get_secret_value() if hasattr(settings.smtp_password, 'get_secret_value') else settings.smtp_password)
        server.send_message(message)
