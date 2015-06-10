'''
Created on June, 2015

@author: sweng66

'''

def sendmail(subject, body_text, receiver):

    import smtplib
    
    server = "localhost"
    sender = 'sgd-programmers@genome.stanford.edu'
        
    message = """\
From: %s
To: %s
Subject: %s

%s
    """ % (sender, ", ".join(receiver), subject, body_text)
    
    try:
        mailer = smtplib.SMTP(server)
        mailer.sendmail(sender, receiver, message)
    except (smtplib.SMTPConnectError):
        print >> stderr, "Error sending email"
        sys.exit(-1)
        






