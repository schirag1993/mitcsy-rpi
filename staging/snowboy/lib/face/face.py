# coding: utf-8

import requests, json
# import cognitive_face as CF
from pprint import pprint
from pathlib import Path
from pymongo import MongoClient
from pymongo import ReturnDocument
from .bingSpeech.speechToText import stt
from .bingSpeech.textToSpeech import tts

def getFaceAPICreds():
    credentials = json.load(open('../credentials.json'))
    faceCreds = credentials['cognitiveServices']['faceDetection']
    return faceCreds

def captureTrainingImages():
    path = Path('trainingImages')
    # Note: The captured images must be named face**.jpeg; 
    # These files must be stored in "./trainingImages"
    # Where ** represents numbers ranging from 00 to 10
    # We need to get eleven images to train the model
    pprint("Images captured!")
    return(path)

def getFaceDetectURL(faceCreds):
    return(faceCreds['endPoint'] + '/detect')

def getFaceIdentifyURL(faceCreds):
    return(faceCreds['endPoint'] + '/identify')

def getPersonGroupURL(faceCreds):
    return(faceCreds['endPoint'] + '/persongroups')

def getFaceKey(faceCreds):
    return(faceCreds['key'])

def checkCountValue(count):
    if(count<10):
        count = "0" + str(count)
        return(count)
    else:
        return(count)

def renameImages(p):
    count = 0
    for file in p.glob('*.jpg'):
        imageCount = checkCountValue(count)
        newImageName = "image" + checkCountValue(count) + ".jpg"
        print("Current file name is: ")
        print(file)
        file.rename(newImageName)
        count = count + 1
        
def createHeaders(subscription_key, contentType):
    headers = {
    'Content-Type': 'application/' + contentType,
    'Ocp-Apim-Subscription-Key': subscription_key,
    }
    return(headers)

def createParams():
    params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,blur,exposure,noise'
    }
    return(params)

def getFaceDetails(res):
    faceId = res.json()[0]['faceId']
    noiseLevel = res.json()[0]['faceAttributes']['noise']['noiseLevel']
    blurLevel = res.json()[0]['faceAttributes']['blur']['blurLevel']
#     all attributes not necessary; for extra functionality later:
    return({
        "faceId" : faceId,
        "noiseLevel" : noiseLevel,
        "blurLevel" : blurLevel
    })

def getFaceId():
    faceCreds = getFaceAPICreds()
    key = getFaceKey(faceCreds)
    headers = createHeaders(key, 'octet-stream')
    params = createParams()
    url = getFaceDetectURL(faceCreds)
    body = open('./target.jpg', 'rb')
    response = requests.post(url=url,data=body,params=params,headers=headers)
    body.close()
    faceID = getFaceDetails(response)['faceId']
    return(faceID)

def createPersonGroup(groupDetails):
    faceCreds = getFaceAPICreds()
    url = getPersonGroupURL(faceCreds)
    fullURL = url + "/" + groupId
    key = getFaceKey(faceCreds)
    headers = createHeaders(key, "json")
    groupId = groupDetails['id']
    groupName = groupDetails['name']
    userData = groupDetails['userData']
    jsonBody = {
        "name" : groupName,
        "userData" : userData
    }
    req = requests.put(url=fullURL, json=jsonBody, headers=headers)
    if(req.status_code == 200):
        print("Successfully created person group")
    else:
        print("Something went wrong with person group creation")
        print("Status code: " + req.status_code + ". Reason: " + req.reason)
    return(req)

# groupDetails = {
#     'id' : 'hospital_department',
#     'name' : 'manipal_orthopedics',
#     'userData' : 'group that manages Manipal hospital patients under the orthopedics department'
# }

def getPersonGroupDetails(personGroupId):
    faceCreds = getFaceAPICreds()
    url = getPersonGroupURL(faceCreds)
    headers = createHeaders(getFaceKey(faceCreds), 'json')
    fullURL = url + "/" + personGroupId
    req = requests.get(url=fullURL, headers=headers)
    if(req.status_code == 200):
        print("Name of group: " + req['name'])
        print("Group ID of group: " + req['personGroupId'])
        print("User data of group: " + req['userData'])
    else:
        print("Error: " + str(req.status_code))
    return(req)

def listPersonGroups():
    faceCreds = getFaceAPICreds()
    key = getFaceKey(faceCreds)
    url = getPersonGroupURL(faceCreds)
    headers = createHeaders(key, 'json')
    req = requests.get(url=url, headers=headers)
    if(req.status_code == 200):
        print("Success")
    else:
        print("Something went wrong with listing person groups")
    return(req)

def getPersonGroupTrainingStatus(personGroupId):
    faceCreds = getFaceAPICreds()
    key = getFaceKey(faceCreds)
    headers = createHeaders(key, 'json')
    url = getPersonGroupURL(faceCreds)
    fullURL = url + '/' + personGroupId + '/training'
    req = requests.get(url=fullURL, headers=headers)
    if(req.status_code != 200):
        print(req.json()['error']['message'])
    else:
        print(req.json()['status'])
    return(req)

def trainPersonGroup(personGroupId):
    faceCreds = getFaceAPICreds()
    key = getFaceKey(faceCreds)
    headers = createHeaders(key, 'json')
    url = getPersonGroupURL(faceCreds)
    fullURL = url + '/' + personGroupId + '/train'
    req = requests.post(url=fullURL, headers=headers)
    if(req.status_code == 202):
        print("Training has begun")
    else:
        print("Something went wrong with training the group")
        print(req.json()['error']['message'])
    return(req)

def createPerson(personGroupId, name, userData):
    faceCreds = getFaceAPICreds()
    key = getFaceKey(faceCreds)
    headers = createHeaders(key, 'json')
    url = getPersonGroupURL(faceCreds)
    fullURL = url + '/' + personGroupId + '/persons'
    body = {
        "name" : name,
        "userData" : userData
    }
    req = requests.post(url=fullURL, headers=headers, json=body)
    if(req.status_code == 200):
        print("Success")
        pprint(req.json())
        dbEntryResult = savePersonId(personGroupId, name, req.json()['personId'])
        if(result.acknowledged):
            print("Stored in DB!")
    else:
        print("Error: " + str(req.status_code))
    return(req)

def getDBCreds():
    credentials = json.load(open('../credentials.json'))
    dbCreds = credentials['database']
    return dbCreds

def connectToDB(dbCreds):
    cosmosConnString = "mongodb://" + dbCreds['username'] + ":" + dbCreds['password'] + "@" + dbCreds['host'] + ":" + str(dbCreds['port']) + "/?ssl=true&replicaSet=globaldb"
    client = MongoClient(cosmosConnString)
    return client

def getClient():
    dbCreds = getDBCreds()
    client = connectToDB(dbCreds)
    return client

def getPatients(client):
    db = client["admin"]
    patientCollection = db["patients"]
    return patientCollection

def savePersonId(personGroupId, name, personId):
    client = getClient()
    patientCollection = getPatients(client)
    dbEntry = {
        "name" : name,
        "personGroupId" : personGroupId,
        "personId" : personId
    }
    result = patientCollection.insert_one(dbEntry)
    print("Person stored successfully")
    return(result)

def addPersonFace(file, personGroupId, personId):
    faceCreds = getFaceAPICreds()
    key = getFaceKey(faceCreds)
    headers = createHeaders(key, 'octet-stream')
    url = getPersonGroupURL(faceCreds)
    fullURL = url + '/' + personGroupId + '/persons/' + personId + '/persistedFaces'
    body = file.read_bytes()
    req = requests.post(url=fullURL, data=body, headers=headers)
    print("Response: " + str(req.status_code) + "; Persisted Face ID: " + req.json()['persistedFaceId'])
    if(req.status_code != 200):
        print("Error: " + pprint(req.json()))
    else:
        print("Success")
        pprint(req.json())
    return(req)
# {'persistedFaceId': '00a07369-b34c-490b-ba2d-c5d9c2a073dd'}

def storePersistedFaceId(persistedFaces, personId):
    client = getClient()
    patientCollection = getPatients(client)
    returnedDoc = patientCollection.find_one_and_update(filter={"personId":personId}, update={"$set" : {"persistedFaces" : persistedFaces}}, upsert=True, return_document=ReturnDocument.AFTER)
    pprint(returnedDoc)
    return(returnedDoc)

def addFaces(personGroupId, personId):
    p = Path('trainingImages')
    # res = addPersonFace(p, "hospital_department", "7234cf7b-2b27-43a7-8fd9-36e131e2fb41")
    persistedFaces = []
    for file in p.glob("*.jpg"):
        res = addPersonFace(file=file, personGroupId=personGroupId, personId=personId)
        persistedFaceId = res.json()['persistedFaceId']
        persistedFaces.append(persistedFaceId)
    pprint(storePersistedFaceId(persistedFaces, personId))
    pprint(persistedFaces)
    print("Faces have been stored")

def moveImages():
    print("Add moving image file code here")

def registerPatient(personGroupId, name, userData):
    path = captureTrainingImages()
#     renameImages(path)
    moveImages()
    response = createPerson(personGroupId, name, userData)
    print("Response from createPerson is: ")
    pprint(response.json())
    print("Created person!")
    addFaces(personGroupId, response.json()['personId'])
    print("Added faces!")
    trainPersonGroup(personGroupId=personGroupId)
    print("Initiated training of group")
    retries = 4
    count = 0
    flag = False
    while(flag!=True):
        print("Count #" + str(count))
        if(count>retries):
            print("Training has commenced but did not finish in the stipulated time. Check again later.")
            flag = True
        req = getPersonGroupTrainingStatus(personGroupId)
        req = req.json()
        if(req['status'] != 'succeeded'):
            if(req['status'] == 'failed'):
                print("Training failed")
                return(False)
            elif(req['status'] == 'running'):
                print("Training is on going. Stand by.")
                count = count + 1
                time.sleep(1)
            elif(req['status'] == 'notstarted'):
                print("Training is yet to begin. Stand by.")
                count = count + 1
                time.sleep(2)
            else:
                print("Training complete!")
                flag = True
                return(True)
        else:
            flag = True
            return(True)
    return(True)

def captureImage():
    # Take a single photo here and rename it as "target.jpg"
    print("Capturing image")
    flag = True
    if(flag):
        print("Image captured!")
        return(True)
    else:
        print("Image capture failed")
        return(False)

def findPatient(personId):
    client = getClient()
    patientCollection = getPatients(client)
    dbResult = patientCollection.find_one({"personId" : personId})
    return(dbResult)

def findPatientRecords(response):
    personId = response[0]['candidates'][0]['personId']
    result = findPatient(personId)
    result = result['name']
    return(result)

def identifyPatient(personGroupId):
    if(captureImage()):
        print("Image prepping for analysis")
    else:
        print("Image capture failed")
        return(False)
    faceIds = []
    faceId = getFaceId()
    faceIds.append(faceId)
    faceCreds = getFaceAPICreds()
    key = getFaceKey(faceCreds)
    url = getFaceIdentifyURL(faceCreds)
    headers = createHeaders(key, 'json')
    body = {
        "faceIds" : faceIds,
        "personGroupId" : personGroupId,
        "maxNumOfCandidatesReturned" : 1,
        "confidenceThreshold" : 0.7
    }
    req = requests.post(url=url, headers=headers, json=body)
    candidate = findPatientRecords(req.json())
    response = "Hello, " + candidate
    return(response)

def getName():
#     name = input("What is your name?")
    askName()
    res = stt('name.wav')
    if(type(res) == tuple):
        if(res[0]):
            print(res[1])
            return(res[1])
    else:
        return(False)

def getAge():
    age = input("What is your age")
    return(age)

def faceHandler(intentAndEntity):
    personGroupId = 'hospital_department'
    intent = intentAndEntity['intent']
    entities = intentAndEntity['entities']
    if(intent == 'medical.registerPatient'):
        #add registration process here
        name = getName()
        age = getAge()
        userData = "{0} is {1} years of age.".format(name, age)
        registerPatient(personGroupId=personGroupId, userData=userData, name=name)
    elif(intent=='medical.identifyPatient'):
        response = identifyPatient(personGroupId)
        print(response)
    else:
        print("I am unable to do that")

