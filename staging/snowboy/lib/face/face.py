import requests, json, re
from pprint import pprint
from pathlib import Path
from pymongo import MongoClient
from pymongo import ReturnDocument
from .bingSpeech.speechToText import stt
from .bingSpeech.textToSpeech import tts, askName, askAge
from .camera.cam import captureTrainingImages, captureTargetImage

def getFaceAPICreds():
    credentials = json.load(open('../credentials.json'))
    faceCreds = credentials['cognitiveServices']['faceDetection']
    return faceCreds

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
    if( len(response.json()) == 0 ):
        return(False)
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
        if(dbEntryResult.acknowledged):
            print("Stored in DB!")
    else:
        print("Error: " + str(req.status_code))
    return(req)

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

def getPatients(client):
    db = client["mitcsy"]
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
    with open(file, 'rb') as body:
        print("File opened")
        req = requests.post(url=fullURL, data=body, headers=headers)
        pprint("Response Code: {}".format(req.status_code))
        if(req.status_code != 200):
            return(False)
        print("Response: " + str(req.status_code) + "; Persisted Face ID: " + req.json()['persistedFaceId'])
        if(req.status_code != 200):
            print("Error: ")
            pprint(req.json())
            return(False)
        else:
            print("Success")
            pprint(req.json())
        return(req)
# {'persistedFaceId': '00a07369-b34c-490b-ba2d-c5d9c2a073dd'}

def storePersistedFaceId(persistedFaces, personId):
    client = getClient()
    print("Inside storePersistedFaceId method")
    patientCollection = getPatients(client)
    returnedDoc = patientCollection.find_one_and_update(filter={"personId":personId}, update={"$set" : {"persistedFaces" : persistedFaces}}, upsert=True, return_document=ReturnDocument.AFTER)
    print("Modified doc is: ")
    pprint(returnedDoc)
    return(returnedDoc)

def addFaces(personGroupId, personId):
    p = Path('.')
    pattern = re.compile('training.*?jpg')
    # res = addPersonFace(p, "hospital_department", "7234cf7b-2b27-43a7-8fd9-36e131e2fb41")
    persistedFaces = []
    for file in p.glob("*.jpg"):
        if(re.search(pattern, str(file))):
            print("File name: {}".format(str(file)))
            print("Adding face to person ID")
            res = addPersonFace(file=str(file), personGroupId=personGroupId, personId=personId)
            if(res == False):
                print("Unable to find face or API error")
                continue
            persistedFaceId = res.json()['persistedFaceId']
            persistedFaces.append(persistedFaceId)
        else:
            print("Unable to find images")
            return(False)
    pprint(storePersistedFaceId(persistedFaces, personId))
    pprint(persistedFaces)
    print("Faces have been stored")

def registerPatient(personGroupId, name, userData):
    print("We will now attempt to capture images to train")
    captureTrainingImages()
    print("Capture complete")
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

def findPatient(personId):
    client = getClient()
    patientCollection = getPatients(client)
    dbResult = patientCollection.find_one({"personId" : personId})
    return(dbResult)

def findPatientRecords(response):
    if(len(response[0]['candidates']) == 0):
        print("No recognized candidates")
        return(False)
    personId = response[0]['candidates'][0]['personId']
    result = findPatient(personId)
    pprint(result)
    if(result):
        result = result['name']
        return(result)
    else:
        print("Unable to find patient")
        return(False)

def identifyPatient(personGroupId):
    if(captureTargetImage()):
        print("Image prepping for analysis")
    else:
        print("Image capture failed")
        return(False)
    faceIds = []
    faceId = getFaceId()
    if(faceId == False):
        return("No faces detected!")
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
    if(candidate == False):
        return("Face does not match any patients or Patient not registered")
    response = "Hello, " + candidate
    return(response)

def getName():
    askName()
    res = stt('patientName.wav')
    if(type(res) != tuple or res[0] == False):
        print("Something went wrong with getting the name")
        return(False)
    else:
        return(res[1])
    
def getAge():
    askAge()
    res = stt('patientAge.wav')
    if(type(res) != tuple or res[0] == False):
        print("Something went wrong with getting the age")
        return(False)
    else:
        return(res[1])

def faceHandler(intentAndEntity):
    print("Inside face handler")
    personGroupId = 'hospital_department'
    intent = intentAndEntity['intent']
    entities = intentAndEntity['entities']
    if(intent == 'medical.registerPatient'):
        print("Inside registerPatient")
        #add registration process here
        name = getName()
        age = getAge()
        if(name == False or age == False):
            print("Something went wrong. Try again.")
            return("Something went wrong. Try again.")
        userData = "{0} is {1} years of age.".format(name, age)
        print(userData)
        registrationStatus = registerPatient(personGroupId=personGroupId, userData=userData, name=name)
        if(registrationStatus):
            return("Successfully registered patient")
    elif(intent=='medical.identifyPatient'):
        response = identifyPatient(personGroupId)
        print(response)
        return(response)
    else:
        print("I am unable to do that")
        return("I am unable to do that")
