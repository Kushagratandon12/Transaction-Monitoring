import smtplib
import numpy as np
import pandas as pd
from io import StringIO
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

Recipients = ['kushagra.tandon@zohomail.eu']

def recipients(recipient):
    data = pd.json_normalize(recipient)
    data = pd.DataFrame(data)
    data = data['email'].tolist()
    data = np.array(data)
    data = data.flatten()
    # ##HERE RES HAS BECOME AN ARRAY ['kushagra.tandon.124@gmail.com' 'samarth.tandon91@gmail.com']
    for i in data:
        Recipients.append(i)
    print(Recipients)
    return


def email_sys(df_orange, df_red):
    orange_file = StringIO()
    orange_file.write(df_orange.to_csv())
    orange_file.seek(0)
    red_file = StringIO()
    red_file.write(df_red.to_csv())
    red_file.seek(0)
    sender_address = 'amlteam.lscg@gmail.com'
    sender_pass = 'lscg2020'
    recipients = Recipients
    message_content = """<!DOCTYPE html>
    <html>
        <body>
            <h2 style="color:Red;">ALERT !!! A Fraud Has Been Detected by LS&CG</h2>
            <h5 style="color:SlateGray;">The Money Laundering Cases Has Been Detected.</h5>
            <img src="cid:Fraudimage" width='400' height=200>
            <h5 style="color:Black;">The Data is Being Attached Along With The Email. Please Look Into The Transaction & Notify On Server</h5>
            <h5 style="color:Black;">Update The Final Result On https://tm.londonscg.co.uk</h5>
            <h6 style="color:Red;">This Is A System Generated Email Please Do Not Reply To This E-Mail. For More Information Contact LS&CG</h6>
        </body>
    </html>
    """
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = ", ".join(recipients)
    message['Subject'] = 'FRAUD DETECTECTION!!!'

    message.attach(MIMEText(message_content, 'html'))
    attach_file_name = red_file
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload(red_file.read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'red', filename='red.txt')
    message.attach(payload)

    # message.attach(MIMEText(message_content, 'html'))
    attach_file_name2 = orange_file
    payload2 = MIMEBase('application', 'octate-stream')
    payload2.set_payload(orange_file.read())
    encoders.encode_base64(payload2)
    payload2.add_header('Content-Decomposition',
                        'orange', filename='orange.txt')
    message.attach(payload2)

    fp = open('data/fraud.jpg', 'rb')
    image = MIMEImage(fp.read())
    fp.close()
    image.add_header('Content-ID', '<Fraudimage>')
    message.attach(image)

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, recipients, text)
    session.quit()
