from django.core.mail import send_mail


class Util:
    @staticmethod
    def send_email(data):
        return send_mail(
            data['email_subject'],
            data['email_body'],
            None,
            [data['email_receiver']])
