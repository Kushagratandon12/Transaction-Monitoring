# In[2]:

from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import pickle
from sklearn.utils import shuffle
print('Build Completed /  No Warnings / Errors ')


# In[3]:


dummy_data = pd.read_excel('DataSets\Dummy_data_testing.xlsx')
# cleaning the dataset
dummy_data_cleaned = dummy_data.drop(
    ['nameOrig', 'nameDest', 'OrigCountry', 'DestCountry'], axis=1)
dummy_data_cleaned = pd.get_dummies(dummy_data_cleaned)
# dummy_data_cleaned.head()
shuffle(dummy_data_cleaned)


# In[4]:


y_dummy = dummy_data_cleaned.loc[:, 'isFraud']
X_dummy = dummy_data_cleaned.drop(['isFraud'], axis=1)


# In[5]:


classifier = RandomForestClassifier(n_estimators=50)
filename = 'TM_Model_Kushagra.h5'
loaded_model = pickle.load(open(filename, 'rb'))
y_pred = loaded_model.predict(X_dummy)


# In[6]:


y_pred


# In[7]:


y_predected_dummy = y_pred
y_predected_dummy = list(y_predected_dummy)
dummy_data = dummy_data.drop('isFraud', axis=1)
dummy_data['isFraud'] = y_predected_dummy
dummy_data


# ## Generating The Orange And Red Segmentation For Data Provided

# In[8]:


# Taking Out Red Identified From The DataSet
df_red = dummy_data[dummy_data['isFraud'] == 1]
df_red = df_red.drop('isFraud', axis=1)
df_red['Flag'] = 'Red'
# Saving the Red File To The CSV Format --------
df_red.to_csv('Generated_Csv\Red_Flagged.csv')


# In[9]:


df2 = pd.read_excel('DataSets\Contries_score.xlsx')
df2 = pd.DataFrame(df2)
df2 = df2.rename(columns={'Overall score': 'score'})
df2 = df2[df2['score'] >= 6]
country_score = pd.Series(df2.score.values, index=df2.Country).to_dict()


# In[10]:


dummy_data = dummy_data[dummy_data['isFraud'] == 0]
dummy_data.drop('isFraud', axis=1)


# In[11]:


orange_flag = {}
green_flag = {}
for i in dummy_data.index:
    if dummy_data['OrigCountry'][i] in country_score.keys() or dummy_data['DestCountry'][i] in country_score.keys():
        if ((dummy_data['amount'][i] > 100000)):
            orange_flag.update({dummy_data['nameOrig'][i]: 'orange'})
    else:
        green_flag.update({dummy_data['nameOrig'][i]: 'green'})


# In[13]:


orange = pd.DataFrame(orange_flag.items(), columns=['nameOrig', 'Flag'])
green = pd.DataFrame(green_flag.items(), columns=['nameOrig', 'Flag'])
df_orange = dummy_data.merge(orange, how="inner")
df_orange.to_csv('Generated_Csv\ORANGE_FLAGGED.csv')
df_green = dummy_data.merge(green, how="inner")
df_green.to_csv('Generated_Csv\Green_Flagged.csv')


# In[14]:


df_orange.to_json('client\src\data\Organge_Flagged.json', orient='records')
df_red.to_json('client\src\data\Red_Flagged.json', orient='records')
df_green.to_json('client\src\data\Green_Flagged.json', orient='records')
