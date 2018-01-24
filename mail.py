import smtplib

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import lxml.etree as ET
from lxml.etree import tostring



path = os.path.dirname(__file__)

def emailOutput(email, configMap, validPlugins):

    # Get the SMTP config
    smtp_server = configMap['global']['smtp']['server']
    smtp_tls = configMap['global']['smtp']['tls']
    smtp_port = configMap['global']['smtp']['port']

    smtp_user = configMap['global']['smtp']['user']
    smtp_pass = configMap['global']['smtp']['password']
    smtp_from = configMap['global']['smtp']['from_addr']
    smtp_cc = configMap['global']['smtp']['cc_addrs']


    email_template_file = configMap['global']['smtp']['template']
    email_to_addr = email
   # email_subject = "Team %s AWS Cost Report for %s to %s" % (team_name,getStartDate(configMap),getEndDate(configMap))
    email_subject= "Signup to your Signiant accounts"


    #for loop here
    values = {}
    for plugin in validPlugins:
        values[plugin['Plugin name']]=plugin['Instruction']

    # insert values
    template = EmailTemplate(template_name=email_template_file, values=values)

    server = MailServer(server_name=smtp_server, username=smtp_user, password=smtp_pass, port=smtp_port, require_starttls=smtp_tls)

    msg = MailMessage(from_email=smtp_from, to_emails=[email_to_addr], cc_emails=smtp_cc,subject=email_subject,template=template)
    send(mail_msg=msg, mail_server=server)
    print("email sent")


# author Dave North
class MailServer(object):
    msg = None

    def __init__(self, server_name='east.EXCH024.serverdata.net', username='<username>', password='<password>', port=587, require_starttls=True):
        self.server_name = server_name
        self.username = username
        self.password = password
        self.port = port
        self.require_starttls = require_starttls

# author Dave North
class EmailTemplate():
    def __init__(self, template_name='', values={}, html=True):
        self.template_name = template_name
        self.values = values
        self.html = html

    def render(self):
        content = open(path +"/" + self.template_name).read()
        #print(len(self.values))
      #  for k,v in self.values.items():
         #   content = content.replace('[%s]' % k,v)

        for k,v in self.values.items():
            tree = ET.fromstring(content, parser=ET.HTMLParser())
            contentnav = tree.find(".//table[@id='main']")
            contentnav.append(ET.XML("<tr><td style='padding: 4px 4px 4px 4px;'><b>"+k+"</b></td><td style='padding: 4px 4px 4px 4px;'>"+v+"</td></tr>"))
            content=tostring(contentnav, encoding="unicode", method="html")
            #print(ET.tostring(tree))
       # content = open(path + "/" + self.template_name, 'w+')
        #content=contentnav
        return content


class MailMessage(object):
    html = False

    def __init__(self, from_email='', to_emails=[], cc_emails=[], subject='', body='', template=None):
        self.from_email = from_email
        self.to_emails = to_emails
        self.cc_emails = cc_emails
        self.subject = subject
        self.template = template
        self.body = body

    def get_message(self):
        if isinstance(self.to_emails, str):
            self.to_emails = [self.to_emails]

        if isinstance(self.cc_emails, str):
            self.cc_emails = [self.cc_emails]

        if len(self.to_emails) == 0 or self.from_email == '':
            raise ValueError('Invalid From or To email address(es)')

        msg = MIMEMultipart('alternative')
        msg['To'] = ', '.join(self.to_emails)
        msg['Cc'] = ', '.join(self.cc_emails)
        msg['From'] = self.from_email
        msg['Subject'] = self.subject
        if self.template:
            #If the template is html, attach and set MIME
            if self.template.html:
                #Attach plain text, which will be used if a template cannot render
                #The last attached element will always take precedence (according to RFC2046)
                msg.attach(MIMEText(self.body, 'plain'))
                msg.attach(MIMEText(self.template.render(),'html'))
            #Otherwise, attach plaintext template
            else:
                msg.attach(MIMEText(self.template.render(),'plain'))
        else:
                msg.attach(MIMEText(self.body, 'plain'))
        return msg

def send(mail_msg, mail_server=MailServer()):
    server = smtplib.SMTP(mail_server.server_name, mail_server.port)
    if mail_server.require_starttls:
        server.starttls()
    if mail_server.username:
        server.login(mail_server.username, mail_server.password)
    server.sendmail(mail_msg.from_email, (mail_msg.to_emails + mail_msg.cc_emails), mail_msg.get_message().as_string())
    server.close()