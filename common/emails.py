from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_email(to: str | list[str], email_type: str, email_data: dict):
    print("AT Task")
    print(email_type)
    print(email_data)

    rendered_email = None

    if email_type == "ACCOUNT_ACTIVATION":
        rendered_email = {
            "html": render_to_string(
                "emails/account_activation.html", 
                context=email_data
            ),
            "subject": "Account Activation"
        }
    elif email_type == "PASSWORD_RESET":
        rendered_email = {
            "html": render_to_string(
                "emails/password_reset.html", 
                context=email_data
            ),
            "subject": "Password Reset"
        }
    elif email_type == "Notification":
        rendered_email = {
            "html": render_to_string(
                "emails/notification.html", 
                context=email_data
            ),
            "subject": "Notification"
        }
    
    if rendered_email is None:
        raise "Email type error"

    print(rendered_email)
    email = EmailMessage(
        rendered_email['subject'],
        rendered_email['html'],
        settings.EMAIL_FROM_ADDRESS,
        to,
        reply_to=settings.EMAIL_REPLY_ADDRESS,
    )
    email.content_subtype = 'html'
    return {'sent_emails_count': email.send()}


class BaseEmail:
    serializer_class = None

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        if serializer_class is None:
            return None
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {}


class Email(BaseEmail):
    name = None

    def __init__(self, to, data=None):
        self.to = to
        self.data = data
        if data is None:
            self.data = {}

    def send(self, due_date=None):
        send_data = None

        serializer = self.get_serializer(data=self.data)
        if serializer:
            serializer.is_valid(raise_exception=True)
            send_data = serializer.data

        # TODO: Handle due_date
        if not due_date:
            if isinstance(self.to, list) or isinstance(self.to, set):
                send_email(self.to, self.name, send_data)
            else:
                send_email((self.to,), self.name, send_data)
        else:
            raise Exception("Due date not implemented yet!")