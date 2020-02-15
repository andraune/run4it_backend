from flask_mail import Message
from run4it.app.extensions import mail


def mail_send_confirmation_code(username, email, code):

    msg = Message('Run4IT Email Confirmation', recipients=[email])
    msg.body = "Hi, {0}!\r\n\r\n".format(username)
	msg.body += "Your confirmation code is: {0}\r\n\r\n".format(code)
    msg.body += "Click the link below to complete your account registration. "
    msg.body += "If the link does not work, you might copy the URL and enter it manually in your browser.\r\n\r\n"
    msg.body += "Activation link: https://run4it.jonnytech.net/confirmation?username={0}&code={1}\r\n\r\n".format(username, code)
    msg.body += "If you haven't tried to register at our site please ignore this email.\r\n\r\nRegards, Jonny//Run4IT-team\r\n"

    with mail.record_messages() as outbox:
        mail.send(msg)
