import os
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
import smtplib
import imaplib
import ssl
import text_decoder


class User:
    """
    The User class controls the properties of the user who sends or receive emails by declaring the user's email
    and password as well as the server and ports to be used for the action.

    Mandatory fields at initialization: user: str() | password: str() | server:str() | port: int()
    """

    def __init__(self, user, password, server, port=None):
        self.user = user
        self.password = password
        self.server = server
        self.port = int(port) if port else None


class Send(User):
    """
    Sends plain and rich text (html) emails with or without attachments.

    Mandatory fields at initialization: user: str() | password: str() | server:str() | port: int()

    Mandatory fields at message: to: list()

    Optional fields at message: cc: list() | bcc: list() | subject: str() | plain: str() | html: str() |
    attach: str() path/to/file

    """

    def __init__(self, user, password, server, port):
        super().__init__(user, password, server, port)
        self.to = list()
        self.cc = list()
        self.bcc = list()
        self.attachment = str()
        self.variable_type_error = "Variable not of list type"
        self.context = ssl.create_default_context()

    def message(self, to, *args, **kwargs):
        message = MIMEMultipart()
        message['From'] = self.user

        if isinstance(to, list):
            self.to = to
        else:
            raise Exception(self.variable_type_error)
        message["To"] = ','.join('to')

        if "subject" in kwargs:
            message['Subject'] = kwargs['subject']

        if "cc" in kwargs:
            if isinstance(kwargs['cc'], list):
                self.cc_mail = kwargs["cc"]
                message['CC'] = ','.join(kwargs['cc'])
            else:
                raise Exception(self.variable_type_error)

        if "bcc" in kwargs:
            if isinstance(kwargs['bcc'], list):
                self.bcc = kwargs['bcc']
                message['Bcc'] = ','.join(kwargs['bcc'])
            else:
                raise Exception(self.variable_type_error)

        # Add body to email
        if 'plain_text' in kwargs:
            message.attach(MIMEText(kwargs["plain_text"], "plain"))

        if 'html' in kwargs:
            message.attach(MIMEText(kwargs['html'], "html"))

        if 'attach' in kwargs:
            filename = kwargs['attach']

            # Open file in binary mode
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)
        self.message = message.as_string()
        self._send()

    def _send(self):
        print('sending email')
        try:
            self.to_email = self.to + self.cc + self.bcc
            server = smtplib.SMTP(self.server, self.port)
            server.ehlo()  # Can be omitted
            server.starttls(context=self.context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(self.user, self.password)
            server.sendmail(self.user, self.to_email, self.message)
        except Exception as e:
            # Print any error messages to stdout
            print(f'ERROR: {e}')
        finally:
            server.quit()
            print('email sent')


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


class Receive(User):
    """
       Receives emails  with or without attachments. The emails are returned as a list of dictionaries,
       the files are stored in a folder under the name of the email subject.

       Mandatory fields at initialization: user: str() | password: str() | server:str()

       Mandatory fields at message: mailbox to search for emails.

       Optional fields at message: number: int() - number of emails to download |
       folder: str()  - name of the parent folder to store the attachment folder.
              """
    def __init__(self, user, password, server):
        super().__init__(user, password, server)
        self.imap = imaplib.IMAP4_SSL(self.server)
        self.imap.login(self.user, self.password)
        self.received_messages = list()

    def messages(self, mailbox, number=3, folder=None):
        status, messages = self.imap.select(mailbox.upper())

        messages = int(messages[0])

        for i in range(messages, messages - number, -1):
            single_message = dict()
            # fetch the email message by ID
            res, msg = self.imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])

                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding) if encoding else subject

                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding) if encoding else From
                        single_message['from'] = From
                        single_message['subject'] = subject
                        # print("Subject:", subject)
                        # print("From:", From)

                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                single_message['body'] = body
                                # print(body)
                            elif "attachment" in content_disposition:
                                # download attachment
                                filename = part.get_filename()
                                if filename:
                                    folder_name = clean(subject)
                                    folder_name = 'folder/' + folder_name if folder else folder_name
                                    if not os.path.isdir(folder_name):
                                        # make a folder for this email (named after the subject)
                                        os.mkdir(folder_name)
                                    filepath = os.path.join(folder_name, filename)
                                    single_message['filepath'] = filepath
                                    # download attachment and save it
                                    try:
                                        open(filepath, "wb").write(part.get_payload(decode=True))
                                    except OSError:
                                        filename = text_decoder.decoding(filename)
                                        filepath = os.path.join(folder_name, filename)
                                        single_message['filepath'] = filepath
                                        open(filepath, "wb").write(part.get_payload(decode=True))
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        # print(f'received Messages{body}')
                        if content_type == "text/plain":
                            # print only text email parts
                            # print(body)
                            single_message['body'] = body
                        if content_type == "text/html":
                            # if it's HTML, create a new HTML file and open it in browser
                            single_message['body'] = body
                            # print(body)
            self.received_messages.append(single_message)
        return(self.received_messages)


    # close the connection and logout
    # imap.close()
    # imap.logout()

