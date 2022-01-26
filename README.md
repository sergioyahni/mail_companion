# mail_companion
An abstraction that helps to send and receive emails using the smtplib and imaplib modules.

Single class to send plain text, HTML email, and attachments

Single class to receive emails and attachments. Emails are received as a list to dictionaries. Attachments are saved
in a forlder of your choice.

## Send Class
Sends plain and rich text (html) emails with or without attachments.

**Mandatory fields at initialization:** 
```
Send(user=str(), password=str(), server=str(), port=int())
```

**Mandatory fields at message:** 
```
Send.message(to=list())
```

**Optional fields at message:**
```
Send.message(to=list(), cc=list(), bcc=list(), subject=str(), plain=str(), html: str(), attach=str(path/to/file))
```
### Send Example
```
from email_agent.mail import Send, Receive

sendmail = Send(user='you@email.com',
                 password='yourpassword',
                 server='smtp.serverofyourchoise.com',
                 port=587)

sendmail.message(to=['whomever@email.com'],
                 cc=['someoneelse@mail.com', 'athirdperson@email.com']
                 subject='Helo, World',
                 html="<h1>Hello, World</h1><h2>I am testing this emailing script</h2><p>Myself</p>")
                 attach='path/to/attachment'
```

## Receive Class
Receive emails  with or without attachments. The emails are returned as a list of dictionaries,
the files are stored in a folder under the name of the email subject.

**Mandatory fields at initialization:** 
```
Receive(user=str(), password=str(), server=str())

```
**Mandatory fields at messages:**
```
Receive.messages(mailbox=str())
```

**Optional fields at message:**
```
Receive.messages(mailbox=str(), number=int(), folder=str())
```
*number* is the number of emails to be downloaded

*folder* is the absolute of relative path to the folder to store the attachments.

All files attached to a message are saved under a directory named after the subject of the message.

###Receive Example
```
receive = Receive(user='you@email.com',
                  password='yourpassword',
                  server='imap.serveryoulike.com')

my_mail = receive.messages(mailbox='inbox', number=5, folder='C:\Users\You\Documents\MyEmails')

for newmail in my_mail:
    print(newmail)
```
