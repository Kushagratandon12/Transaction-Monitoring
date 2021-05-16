import pickle
import pandas as pd
import pycountry_convert as pc
from components.utils import email_sys

SUSPECTED_TRANSACTION_VALUE = 100000


def country_to_continent(country_name):
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    country_continent_code = pc.country_alpha2_to_continent_code(
        country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(
        country_continent_code)
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
    # THE MODEL FILE NAME IS TM_Model_Kushagra FOR DUMMY-DATA
    # Continent Generation

    source_countries = data['OrigCountry']
    source_countries = source_countries.array
    # print(source_countries)
    source_countries = [s.lower() for s in source_countries]
    map_continent = []

    # convert country to continent
    for country in source_countries:
        country = country.title()
        data_country = country_to_continent(country)
        map_continent.append(data_country)

    map_continent = list(pd.Series(map_continent))
    print(type(data))
    data['OrigContinent'] = map_continent
    ####################
    filename = 'components/model/TM_Model_Kushagra.h5'
    loaded_model = pickle.load(open(filename, 'rb'))
    y_pred = loaded_model.predict(data_cleaned)
    # MODEL PREDICTIONS DONE ABOVE AND NOW ADDING THE PREDICECTED Data TO THE DUMMY DATASET FOR WORK
    y_predicted = list(y_pred)
    data['isFraud'] = y_predicted
    # RED FLAGGING THE PREDICECTED SYSTEM
    df_red = data[data['isFraud'] == 1]
    df_red = df_red.drop('isFraud', axis=1)
    df_red['Flag'] = 'red'
    # CHECKING FOR THE ORANGE AND GREEN FLAG
    df2 = pd.DataFrame(pd.read_excel('/components/model/Contries_score.xlsx'))
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
    send = [df_red, df_orange, df_green]
    result = pd.concat(send).to_json(orient='records')
    print(result)
    # Email Notification System
    email_sys(df_red, df_orange)
    return result


def process2(json):
    data = pd.DataFrame(json)
    data_cleaned = data.drop(
        ['nameOrig', 'nameDest', 'OrigCountry', 'DestCountry', 'type'], axis=1)
    # Continent Generation

    source_countries = data['OrigCountry']
    source_countries = source_countries.array
    # print(source_countries)
    source_countries = [s.lower() for s in source_countries]
    map_continent = []

    # convert country to continent
    for country in source_countries:
        country = country.title()
        data_country = country_to_continent(country)
        map_continent.append(data_country)

    map_continent = list(pd.Series(map_continent))
    print(type(data))
    data['OrigContinent'] = map_continent
    ####################
    # THE MODEL FILE NAME IS TM_Model_Kushagra FOR DUMMY-DATA
    filename = 'components/model/TM_Model_Kushagra2.h5'
    loaded_model = pickle.load(open(filename, 'rb'))
    y_pred = loaded_model.predict(data_cleaned)
    # MODEL PREDICTIONS DONE ABOVE AND NOW ADDING THE PREDICECTED Data TO THE DUMMY DATASET FOR WORK
    y_predicted = list(y_pred)
    data['isFraud'] = y_predicted
    # RED FLAGGING THE PREDICECTED SYSTEM
    df_red = data[data['isFraud'] == 1]
    df_red = df_red.drop('isFraud', axis=1)
    df_red['Flag'] = 'red'
    # CHECKING FOR THE ORANGE AND GREEN FLAG
    df2 = pd.DataFrame(pd.read_excel('/components/model/Contries_score.xlsx'))
    df2 = df2.rename(columns={'Overall score': 'score'})
    df2 = df2[df2['score'] >= 6]
    country_score = pd.Series(df2.score.values, index=df2.Country).to_dict()

    data = data[data['isFraud'] == 0]
    data = data.drop('isFraud', axis=1)
    orange_flag = {}
    green_flag = {}
    for i in data.index:
        if data['OrigCountry'][i] in country_score.keys() or data['DestCountry'][i] in country_score.keys():
            if ((float(data['amount'][i]) > SUSPECTED_TRANSACTION_VALUE)):
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
    email_sys(df_orange, df_red)
    return result

# Email Notification System
