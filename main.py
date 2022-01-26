from email_agent.mail import Send, Receive

sendmail = Send(user='you@email.com',
                 password='yourpassword',
                 server='smtp.serverofyourchoise.com',
                 port=587)

sendmail.message(to=['whomever@email.com'],
                 cc=['someoneelse@mail.com', 'athirdperson@email.com'],
                 subject='Hello, World',
                 html="<h1>Hello, World</h1><h2>I am testing this emailing script</h2><p>Myself</p>",
                 attach='path\\to\\attachment')


receive = Receive(user='you@email.com',
                  password='yourpassword',
                  server='imap.serveryoulike.com')

my_mail = receive.messages(mailbox='inbox', number=5, folder='C:\\Users\\You\\Documents\\MyEmails')

for newmail in my_mail:
    print(newmail)
