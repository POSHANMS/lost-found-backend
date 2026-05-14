from flask_mail import Message
from extensions import mail

def send_claim_notification(to_email, item_title, claimant_name):
    """
    Sends email to item owner when someone claims their item.
    to_email     → item owner's email
    item_title   → name of the item being claimed
    claimant_name → name of the person who made the claim
    """
    msg = Message(
        subject=f"Someone claimed your item: {item_title}",
        recipients=[to_email],
        body=f"""
Hello,

{claimant_name} has submitted a claim for your item: {item_title}

Please log in to FindIt to review the claim and approve or reject it.

Thank you,
FindIt Team
        """
    )
    mail.send(msg)

def send_claim_response(to_email, item_title, status):
    """
    Sends email to claimant when their claim is approved or rejected.
    to_email   → claimant's email
    item_title → name of the item they claimed
    status     → "approved" or "rejected"
    """
    msg = Message(
        subject=f"Your claim for '{item_title}' was {status}",
        recipients=[to_email],
        body=f"""
Hello,

Your claim for the item '{item_title}' has been {status}.

{"Congratulations! Please coordinate with the item owner to collect your item." if status == "approved" else "Unfortunately your claim was not approved. You may try claiming other items."}

Thank you,
FindIt Team
        """
    )
    mail.send(msg)

def send_welcome_email(to_email, name):
    """
    Sends welcome email when a new user registers.
    """
    msg = Message(
        subject="Welcome to FindIt!",
        recipients=[to_email],
        body=f"""
Hello {name},

Welcome to FindIt — your campus lost and found portal.

You can now:
- Post lost or found items
- Browse all reported items
- Claim items that belong to you

Thank you for joining,
FindIt Team
        """
    )
    mail.send(msg)