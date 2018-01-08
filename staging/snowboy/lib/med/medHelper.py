from pymongo import MongoClient
import json, os, re
# import pandas as pd
from pprint import pprint
from .bingSpeech.textToSpeech import tts
from .bingSpeech.speechToText import stt, DiagnoseSTT
from .audioRecorderAutoStop import record_to_file

# def getDBCreds():
#     credentials = json.load(open('../credentials.json'))
#     dbCreds = credentials['database']
#     return dbCreds

def getDBCreds():
    credentials = json.load(open('../credentials.json'))
    dbCreds = credentials['database2']
    return dbCreds

# def connectToDB(dbCreds):
#     cosmosConnString = "mongodb://" + dbCreds['username'] + ":" + dbCreds['password'] + "@" + dbCreds['host'] + ":" + str(dbCreds['port']) + "/?ssl=true&replicaSet=globaldb"
#     client = MongoClient(cosmosConnString)
#     return client

def connectToDB(dbCreds):
    mongoConnString = "mongodb://" + dbCreds['username'] + ":" + dbCreds['password'] + "@" + dbCreds['host'] + ":" + str(dbCreds['port']) + '/' + dbCreds['dbName']
#     mongoConnString = "mongodb://{0}:{1}@{2}:{3}/{4}".format(dbCreds['username'], dbCreds['password'], dbCreds['host'], str(dbCreds['port']), dbCreds['dbName'])
    client = MongoClient(mongoConnString)
    return client

def getClient():
    dbCreds = getDBCreds()
    client = connectToDB(dbCreds)
    return client

def getLiterature(client):
    db = client["mitcsy"]
    literatureCollection = db["literatures"]
    return literatureCollection

def getSymptomList(client):
    db = client['mitcsy']
    symptomCollection = db['symptoms']
    symptomListCursor = symptomCollection.find(filter={})
    symptomList = []
    for element in symptomListCursor:
        symptomList.append(element['name'])
    return symptomList

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

def diagnoseDisease(client):
    print("Getting symptom list")
    symptomList = getSymptomList(client)
    print("Got symptom list")
    response = diagnoseDiseaseHelper(symptomList, client)
    return(response)

def diagnoseDiseaseHelper(symptomList, client):
    tts('We will now attempt to diagnose your disease')
    question = "Do you have {0} ?"
    flag = False
    targetSymptoms = []
    nonTargetSymptoms = []
    symptomListLength = len(symptomList)
    count = 0
    ans = "no"
    while(flag !=True):
        for symptom in symptomList:
            tts(question.format(symptom))
            print("Calling record function")
            record_to_file("symptom.wav")
            print("Returned from record function")
            sttRes = DiagnoseSTT()
            if(type(sttRes) != tuple):
                print("Something went wrong!");
                tts("Something went wrong, try again later")
                return
            elif(sttRes[0] != True):
                print("STT returned the following: {0}".format(sttRes[1]))
                tts(sttRes[1])
            else:
                questionResponse = sttRes[1]
                questionResponse = questionResponse.split()
                print("questionResponse is: ")
                pprint(questionResponse)
                if('yes' in questionResponse or 'yeah' in questionResponse or 'definitely' in questionResponse or 'Yes' in questionResponse or 'Yes.' in questionResponse or 'Yeah.' in questionResponse):
                    print("Found a yes!")
                    ans = "yes"
                else:
                    print("Found a no!")
                    ans = "no"
            print("Processing")
            if(ans == 'yes'):
                targetSymptoms.append(symptom)
#                 client, symptoms, nonTargetSymptoms, targetSymptomCount, nonTargetSymptomCount
                queryResult = getDiseaseList(client=client, symptoms=targetSymptoms, nonTargetSymptoms=nonTargetSymptoms, targetSymptomCount=len(targetSymptoms), nonTargetSymptomCount=len(nonTargetSymptoms))
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
                lenNonTargetSymptoms = len(nonTargetSymptoms)
                queryResult = getDiseaseList(client=client, symptoms=targetSymptoms, nonTargetSymptoms=nonTargetSymptoms, targetSymptomCount=len(targetSymptoms), nonTargetSymptomCount=len(nonTargetSymptoms))
                if(queryResult['count']==0):
                    flag = True
                    response = "It seems the symptoms do not match anything from the database"
                    return(response)

def findSymptoms(diseaseName, client):
    literatureCollection = getLiterature(client)
    result = literatureCollection.find_one(filter={"title" : diseaseName})
    symptoms = ""
    for symptom in result["symptoms"]:
        symptoms = symptoms + ", " + symptom
    response = "The symptoms of " + diseaseName + " are " + symptoms + "."
    return response

def findDescription(diseaseName, client):
    literatureCollection = getLiterature(client)
    result = literatureCollection.find_one(filter={"title" : diseaseName})
    diseaseDescription = result["content"]
    return diseaseDescription

def medicalQuery(luisRes):
    intent = luisRes['intent']
    entities = luisRes['entities']
    print("Entities are: ")
    pprint(entities)
    dbClient = getClient()
    if(intent == 'medical.getDescription'):
        if(len(entities) == 0):
            return("Could not identify disease in statement. Please try again.")
        else:
            return(findDescription(entities[0]['diseaseName'], dbClient))
    elif(intent == 'medical.findDisease'):
        return(diagnoseDisease(dbClient))
    elif(intent == 'medical.getSymptoms'):
        if(len(entities) == 0):
            return("Unable to find the disease in statement. Please try again.")
        else:
            return(findSymptoms(entities[0]['diseaseName'], dbClient))
        # //////////////^MODIFY MAIN CODE FOR THIS^\\\\\\\\\\\\\\\\