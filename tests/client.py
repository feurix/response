#!/usr/bin/env python

'''Simple LMTP client implementation to test response-lmtp'''

import sys
import smtplib

from email.mime.text import MIMEText

if len(sys.argv) < 4 or \
  (len(sys.argv) > 4 and len(sys.argv) < 6):
    print('Usage: %s FROM TO SUBJECT [HEADER_NAME HEADER_VALUE]' % sys.argv[0])
    sys.exit(1)

msg = MIMEText(
'''This is a TEST
body in text/plain.

Best regards,
John
''')

msg['From'] = sys.argv[1]
msg['To'] = sys.argv[2].split('@',1)[0].replace('#','@')
msg['Subject'] = sys.argv[3]

try:
    if sys.argv[4]:
        msg.add_header(sys.argv[4], sys.argv[5])
except:
    pass

print(
'''

Message length is %s
Sending message...

''' % repr(len(msg.as_string())))

server = smtplib.LMTP('localhost', 10024)
server.set_debuglevel(1)
server.sendmail(sys.argv[1], sys.argv[2], msg.as_string())
server.quit()

