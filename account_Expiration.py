#!/usr/bin/env python3
# -*- conding: utf-8 -*-
#Author Michael.Wang

from datetime import datetime, timedelta, timezone
from pprint import pprint
from ldap3 import Server, Connection, SUBTREE, ALL
import sys
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib
import time


#Provide the LDAP Bind Info
LDAP_HOST="10.1.10.1"
LDAP_PORT=389
LDAP_USER="michaeladmin"
LDAP_PASS="********"
PwdWarnDays = 14
PwdMaxAge = 90

#Get LDAP User Details
def search(filter='(&(objectclass=person))', basedn='OU=OAUser,DC=qxic,DC=net'):
    with Connection(Server(LDAP_HOST, port=LDAP_PORT), user=LDAP_USER, password=LDAP_PASS) as ldap:
        ldap.search(basedn, filter, attributes=['name', 'mail', 'pwdLastSet']) 
        return ldap.entries

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def sendMail(to_addr, expir_date, name, from_addr='ITAccount@qxic.net'):
    try:
        smtp_server='10.1.10.11'
        body="{}，您的密码将在{}天后过期，请抓紧时间修改您的密码".format(name, expir_date)
        print(body)
        msg = MIMEText(body, 'html', 'utf-8')
        msg['From']=_format_addr('账号管理员 <%s>' % from_addr)
        msg['To']=_format_addr('用户 <%s>' % to_addr)
        #msg['From']='Michael.Wang@qxic.net'
        #msg['To']=to_addr
        msg['Subject']=Header('密码过期提醒', 'utf-8').encode()
        server=smtplib.SMTP(smtp_server)
        #server=smtplib.SMTP(smtp_server, 465)
        #server.set_debuglevel(1)
        #server.ehlo()
        #server.starttls()
        #server.login(from_addr, password)
        print(msg.as_string())
        #server.sendmail(from_addr, [to_addr], msg.as_string())
        server.send_message(msg)
        server.quit()
    except Exception as ex:
        raise(ex)

for user in search():
    name = user.name
    emailAddress = user.mail
    delta = (datetime.now(timezone.utc) - user.pwdLastSet.value).days
    expirIn = PwdMaxAge - delta
    if expirIn <= PwdWarnDays:
        #print('%s, your password will expired in %s days' % (name, expirIn))
        sendMail('Michael.Wang@qxic.net', expirIn, name)
        time.sleep(1)
