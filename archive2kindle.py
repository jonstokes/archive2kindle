#!/usr/local/bin/python3
# encoding: utf-8

# Install: pipenv install requests bs4 --python 3
# Usage: python mailer.py https://arxiv.org/abs/1805.12076
# Always supply an arxiv ABS page!!!

import sys
import os
import smtplib
import requests
import yaml
from bs4 import BeautifulSoup
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

COMMASPACE = ', '


def send_file(path):
    with open('/Users/jstokes/.archive2kindle/secrets.yml', 'r') as file: 
        secrets = yaml.load(file, Loader=yaml.FullLoader)

    sender = secrets['sender']
    gmail_password = secrets['gmail_password']
    recipients = secrets['recipients']
    
    outer = MIMEMultipart()
    outer['Subject'] = 'convert'
    outer['To'] = COMMASPACE.join(recipients)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # List of attachments
    attachments = [path]

    # Add the attachments to the message
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            outer.attach(msg)
        except:
            print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
            raise

    composed = outer.as_string()

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(sender, gmail_password)
            s.sendmail(sender, recipients, composed)
            s.close()
        print("Email sent!")
    except:
        print("Unable to send the email. Error: ", sys.exc_info()[0])
        raise


if __name__ == '__main__':
    url = sys.argv[1]
    if 'arxiv.org' in url and '.pdf' in url:
        url = url.replace('.pdf', '')
        url = 'https://arxiv.org/abs/' + url.split('/')[-1]
    if 'abs' in url:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        t = soup.find('h1', attrs={"class": "title"})
        t = t.text.replace('Title:', '').strip()
        url = 'https://arxiv.org/pdf/' + url.split('/')[-1] + '.pdf'
        fname = t + '.pdf'
    else:
        fname = url.split('/')[-1]

    print('Downloading', url)
    print(fname)
    r = requests.get(url, allow_redirects=True)
    with open(fname, 'wb') as fl:
        fl.write(r.content)

    print('Sending', url)
    send_file(fname)
    print('Removing temp file')
    os.remove(fname)
    print('Done')
