import pandas as pd
import json
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from io import StringIO
import base64
from email import encoders
import smtplib
import pickle
import pycountry_convert as pc

SUSPECTED_TRANSACTION_VALUE = 100000
Recipients = ['kushagra.tandon@zohomail.eu' , 'kushagra.25@zohomail.eu']


def country_to_continent(country_name):
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name

def process(json):
    data = pd.json_normalize(json)
    #data = data.drop(['isFraud'], axis=1)
    data['amount'] = data['amount'].astype(float)
    data['oldbalanceOrg'] = data['oldbalanceOrg'].astype(float)
    data['newbalanceOrig'] = data['newbalanceOrig'].astype(float)
    data['oldbalanceDest'] = data['oldbalanceDest'].astype(float)
    data['newbalanceDest'] = data['newbalanceDest'].astype(float)
    data_cleaned = data.drop(
        ['nameOrig', 'nameDest', 'OrigCountry', 'DestCountry'], axis=1)
    data_cleaned = pd.get_dummies(data_cleaned)
    #THE MODEL FILE NAME IS TM_Model_Kushagra FOR DUMMY-DATA
    ##Continent Generation

    source_countries = data['OrigCountry']
    source_countries = source_countries.array
    # print(source_countries)
    source_countries = [s.lower() for s in source_countries]
    map_continent = []

    # convert country to continent
    for country in source_countries:
        country = country.title()
        data_country= country_to_continent(country)
        map_continent.append(data_country)

    map_continent = list(pd.Series(map_continent))
    print(type(data))
    data['OrigContinent'] = map_continent
    ####################
    filename = 'data/TM_Model_Kushagra.h5'
    loaded_model = pickle.load(open(filename, 'rb'))
    y_pred = loaded_model.predict(data_cleaned)
    #MODEL PREDICTIONS DONE ABOVE AND NOW ADDING THE PREDICECTED Data TO THE DUMMY DATASET FOR WORK
    y_predicted = list(y_pred)
    data['isFraud'] = y_predicted
    #RED FLAGGING THE PREDICECTED SYSTEM
    df_red = data[data['isFraud'] == 1]
    df_red = df_red.drop('isFraud', axis=1)
    df_red['Flag'] = 'red'
    #CHECKING FOR THE ORANGE AND GREEN FLAG
    df2 = pd.DataFrame(pd.read_excel('data/Contries_score.xlsx'))
    df2 = df2.rename(columns={'Overall score': 'score'})
    df2 = df2[df2['score'] >= 6]
    country_score = pd.Series(df2.score.values, index=df2.Country).to_dict()

    data = data[data['isFraud'] == 0]
    data = data.drop('isFraud', axis=1)
    print(type(data))
    orange_flag = {}
    green_flag = {}
    for i in data.index:
        if data['OrigCountry'][i] in country_score.keys() or data['DestCountry'][i] in country_score.keys():
            if ((data['amount'][i] > SUSPECTED_TRANSACTION_VALUE)):
                orange_flag.update({data['nameOrig'][i]: 'orange'})
            else:
                green_flag.update({data['nameOrig'][i]: 'green'})
        else:
            green_flag.update({data['nameOrig'][i]: 'green'})

    orange = pd.DataFrame(orange_flag.items(), columns=['nameOrig', 'Flag'])
    green = pd.DataFrame(green_flag.items(), columns=['nameOrig', 'Flag'])
    df_orange = data.merge(orange, how="inner")
    df_green = data.merge(green, how="inner")
    # print(df_orange)
    # print(df_green)
    # print(df_red)
    send = [df_red, df_orange, df_green]
    result = pd.concat(send).to_json(orient='records')
    print(result)
    # Email Notification System
    email_sys(df_red,df_orange)
    return result

def process2(json):
    data=pd.DataFrame(json)
    data_cleaned = data.drop(
        ['nameOrig', 'nameDest', 'OrigCountry', 'DestCountry','type'], axis=1)
    ##Continent Generation

    source_countries = data['OrigCountry']
    source_countries = source_countries.array
    # print(source_countries)
    source_countries = [s.lower() for s in source_countries]
    map_continent = []

    # convert country to continent
    for country in source_countries:
        country = country.title()
        data_country= country_to_continent(country)
        map_continent.append(data_country)

    map_continent = list(pd.Series(map_continent))
    print(type(data))
    data['OrigContinent'] = map_continent
    ####################
    #THE MODEL FILE NAME IS TM_Model_Kushagra FOR DUMMY-DATA 
    filename = 'data/TM_Model_Kushagra2.h5'
    loaded_model = pickle.load(open(filename, 'rb'))
    y_pred = loaded_model.predict(data_cleaned)
    #MODEL PREDICTIONS DONE ABOVE AND NOW ADDING THE PREDICECTED Data TO THE DUMMY DATASET FOR WORK
    y_predicted = list(y_pred)
    data['isFraud'] = y_predicted
    #RED FLAGGING THE PREDICECTED SYSTEM
    df_red = data[data['isFraud'] == 1]
    df_red = df_red.drop('isFraud', axis=1)
    df_red['Flag'] = 'red'
    #CHECKING FOR THE ORANGE AND GREEN FLAG
    df2 = pd.DataFrame(pd.read_excel('data/Contries_score.xlsx'))
    df2 = df2.rename(columns={'Overall score': 'score'})
    df2 = df2[df2['score'] >= 6]
    country_score = pd.Series(df2.score.values, index=df2.Country).to_dict()

    data = data[data['isFraud'] == 0]
    data=data.drop('isFraud', axis=1)
    orange_flag = {}
    green_flag = {}
    for i in data.index:
        if data['OrigCountry'][i] in country_score.keys() or data['DestCountry'][i] in country_score.keys():
            if (( float(data['amount'][i]) > SUSPECTED_TRANSACTION_VALUE)):
                orange_flag.update({data['nameOrig'][i]: 'orange'})
            else:
                green_flag.update({data['nameOrig'][i]: 'green'})
        else:
            green_flag.update({data['nameOrig'][i]: 'green'})

    orange = pd.DataFrame(orange_flag.items(), columns=['nameOrig', 'Flag'])
    green = pd.DataFrame(green_flag.items(), columns=['nameOrig', 'Flag'])
    df_orange = data.merge(orange, how="inner")
    df_green = data.merge(green, how="inner")
    # print(df_orange)
    # print(df_green)
    send = [df_red, df_orange, df_green]
    result = pd.concat(send).to_json(orient='records')
    print(result)
    email_sys(df_orange,df_red)
    return result

#Email Notification System
def recipients(recipient):
    data = pd.json_normalize(recipient)
    data = pd.DataFrame(data)
    data = data['email'].tolist()
    data=np.array(data)
    data = data.flatten()
    # print(data)
    # ##HERE RES HAS BECOME AN ARRAY ['kushagra.tandon.124@gmail.com' 'samarth.tandon91@gmail.com']
    for i in data:
        Recipients.append(i)
    print(Recipients)
    return

def email_sys(df_orange,df_red):
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
    payload2.add_header('Content-Decomposition', 'orange', filename='orange.txt')
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
