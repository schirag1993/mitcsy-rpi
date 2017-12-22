
# coding: utf-8

# ## Libraries:

# In[298]:


from pymongo import MongoClient
import json, os
# import pandas as pd
from pprint import pprint
from .camera.cam import captureTrainingImages


# # Helper Functions

# ### DB Helper Functions:

# In[4]:


def getDBCreds():
    credentials = json.load(open('../credentials.json'))
    dbCreds = credentials['database']
    return dbCreds


# In[6]:


def connectToDB(dbCreds):
    cosmosConnString = "mongodb://" + dbCreds['username'] + ":" + dbCreds['password'] + "@" + dbCreds['host'] + ":" + str(dbCreds['port']) + "/?ssl=true&replicaSet=globaldb"
    client = MongoClient(cosmosConnString)
    return client


# In[3]:


def getClient():
    dbCreds = getDBCreds()
    client = connectToDB(dbCreds)
    return client


# ### Disease Helper Funtions:

# In[1]:


def getLiterature(client):
    db = client["admin"]
    literatureCollection = db["literatures"]
    return literatureCollection


# In[108]:


def getSymptomList(client):
    db = client['admin']
    symptomCollection = db['symptoms']
    symptomListCursor = symptomCollection.find(filter={})
    symptomList = []
    for element in symptomListCursor:
        symptomList.append(element['name'])
    return symptomList


# In[302]:


def getDiseaseList(client, symptoms, nonTargetSymptoms, targetSymptomCount, nonTargetSymptomCount):
    literatureCollection = getLiterature(client)
    if(targetSymptomCount==0):
        diseaseList = literatureCollection.find(filter={"symptoms" : {"$nin" : nonTargetSymptoms}})
    else:
        diseaseList = literatureCollection.find(filter={"symptoms" : {"$all" : symptoms, "$nin" : nonTargetSymptoms}})
    count = 0
    diseases = []
    for disease in diseaseList:
        count = count + 1
        diseases.append(disease['title'])
    return({"diseases":diseases,"count":count})


# ### The following code segment showcases how pandas can be used for better symptom analysis

# In[1]:


# symptomList = getSymptomList(client)
# dfColumns = ["True"]

# symptomDf = pd.DataFrame(index=testSymptomList, columns=dfColumns)

# symptomDf = testDf.fillna(0)
# targetSymptoms = []
# for index,row in testDf.iterrows():
#     if(row.iloc[0] == 1):
#         print("Adding symptom to targetSymptom list")
#         print(row.name)
#         ***modify df here to generate a sparse matrix***
#         validSymptoms.append(row.name)


# ### **%%%End of Sample Code Block%%%**

# In[5]:


def diagnoseDisease(symptomList, client):
    flag = False
    targetSymptoms = []
    nonTargetSymptoms = []
    symptomListLength = len(symptomList)
    count = 0
    while(flag !=True):
        for symptom in symptomList:
            ans = input("Do you have " + symptom + "? \n")
            if(ans == 'yes'):
                targetSymptoms.append(symptom)
                queryResult = getDiseaseList(targetSymptoms, nonTargetSymptoms, len(targetSymptoms), len(nonTargetSymptoms))
                if(queryResult['count']==1):
                    flag = True
                    response = "The diagnosed disease is " + queryResult['diseases'][0]
                    return(response)
                if(queryResult['count']==0):
                    flag = True
                    response = "It seems the symptoms do not match anything from the database"
                    return(response)
            else:
                nonTargetSymptoms.append(symptom)
                queryResult = getDiseaseList(targetSymptoms, nonTargetSymptoms, len(targetSymptoms), len(nonTargetSymptoms))
                if(queryResult['count']==0):
                    flag = True
                    response = "It seems the symptoms do not match anything from the database"
                    return(response)


# In[4]:


def findSymptoms(diseaseName, client):
    literatureCollection = getLiterature(client)
    result = literatureCollection.find_one(filter={"title" : diseaseName})
    symptoms = ""
    for symptom in result["symptoms"]:
        symptoms = symptoms + ", " + symptom
    response = "The symptoms of " + diseaseName + " are " + symptoms + "."
    return response


# In[2]:


def findDescription(diseaseName, client):
    literatureCollection = getLiterature(client)
    result = literatureCollection.find_one(filter={"title" : diseaseName})
    diseaseDescription = result["content"]
    return diseaseDescription


def medicalQuery(luisRes):
    intent = luisRes['intent']
    entities = luisRes['entities']
    dbClient = getClient()
    if(intent == 'medical.getDescription'):
        return(findDescription(entities[0]['diseaseName'], dbClient))
    elif(intent == 'medical.findDisease'):
        return("Functionality unavailable")
    elif(intent == 'medical.getSymptoms'):
        return(findSymptoms(entities[0]['diseaseName'], dbClient))
        # //////////////^MODIFY MAIN CODE FOR THIS^\\\\\\\\\\\\\\\\
