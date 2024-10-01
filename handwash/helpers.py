from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

def send_forget_password_mail(email, token,userid):
    subject = 'Your forget password link'
    html_message = f'''
    <html>
    <body>
        <p>Hi,</p>
        <p>Click on the link below to reset your password:</p>
        <p><a href="http://127.0.0.1:8000/change-password/{token}/{userid}/">Reset Password</a></p>
    </body>
    </html>
    '''
    plain_message = strip_tags(html_message)  # Convert HTML to plain text
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(
        subject,
        plain_message,
        email_from,
        recipient_list,
        html_message=html_message,
    )
    return True

def sendCheckoutMail(email, order_id):
    subject = 'Your order has been placed'
    html_message = f'''
    <html>
    <body>
        <p>Hi,</p>
        <p>Your order has been placed successfully. Your order ID is {order_id}.</p>
        <p>Thank you for shopping with us!</p>
    </body>
    </html>
    '''
    plain_message = strip_tags(html_message)  # Convert HTML to plain text
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(
        subject,
        plain_message,
        email_from,
        recipient_list,
        html_message=html_message,
    )
    return True