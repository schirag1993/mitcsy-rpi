import requests, json, nltk
from .audioRecorderAutoStop import record_to_file
from .bingSpeech.speechToText import stt
from .bingSpeech.textToSpeech import tts
from pprint import pprint
from pymongo import MongoClient

def getMailGunCreds():
    credentials = json.load(open('../credentials.json'))
    mailGunCreds = credentials['mailgun']
    return mailGunCreds

def removePunc(s):
    nltk.download('punkt')
    words = nltk.word_tokenize(s)
    words=[word.lower() for word in words if word.isalpha()]
    sentence = ""
    count = 0
    for word in words:
        if(count == 0):
            sentence = word
        else:
            sentence = sentence + " " + word
        count = count + 1
    return(sentence)

def getDBCreds():
    credentials = json.load(open('../credentials.json'))
    dbCreds = credentials['database2']
    return dbCreds

def connectToDB(dbCreds):
    mongoConnString = "mongodb://" + dbCreds['username'] + ":" + dbCreds['password'] + "@" + dbCreds['host'] + ":" + str(dbCreds['port']) + '/' + dbCreds['dbName']
#     mongoConnString = "mongodb://{0}:{1}@{2}:{3}/{4}".format(dbCreds['username'], dbCreds['password'], dbCreds['host'], str(dbCreds['port']), dbCreds['dbName'])
    client = MongoClient(mongoConnString)
    return client

def getClient():
    dbCreds = getDBCreds()
    client = connectToDB(dbCreds)
    return client

def getDocCollection(client):
    db = client["mitcsy"]
    docCollection = db["doctors"]
    return docCollection

def getMailID(name):
    cleanedName = removePunc(name)
    print("Cleaned name is: {}".format(cleanedName))
    client = getClient()
    docCollection = getDocCollection(client)
    record = docCollection.find_one(filter={'name':cleanedName})
    print("Full record is: {}".format(record))
    if(record):
        return(record['mail'])
    else:
        print("Mail ID for specified name not found in DB")
        return(False)
    
def sendMail(data):
    mailGunCreds = getMailGunCreds()
    url = mailGunCreds['url']
    auth=("api", mailGunCreds['apiKey'])
    response = requests.post(url=url, auth=auth, data=data)
    if(response.status_code == 200):
        print("Success!")
        return("Successfully sent mail")
    else:
        return("Failed to send mail. Try again later")
    
def getMailDetails():
    tts("What shall I enter as the subject?")
    record_to_file('mailSubject.wav')
    sub = stt('mailSubject.wav')
    if(sub[0] == False):
        print("Note: Error in STT while obtaining subject")
        sub = False
        return((False, False, False))
    tts('Whom should the mail be sent to?')
    record_to_file('mailTo.wav')
    mailTo = stt('mailTo.wav')
    if(mailTo[0] == False):
        print("Error in STT while obtaining email address to send to.")
        mailTo = False
        return((False, False, False))
    tts('What should be in the body?')
    record_to_file('mailBody.wav')
    body = stt('mailBody.wav')
    if(body[0] == False):
        print("Error in STT while obtaining body of mail")
        body = False
        return((False, False, False))
    mailDetails = (mailTo[1], sub[1], body[1])
    return(mailDetails)

def createMail():
    toMail, subject, body = getMailDetails()
    mailId = getMailID(toMail)
    if(mailId == False):
        print("Mail ID not found")
        return(False)
    fromMail = "Mailgun Sandbox <postmaster@sandbox62818be204d9434b94235950b924fb19.mailgun.org>"
    data = {
        "from" : fromMail,
        "to" : mailId,
        "subject" : subject,
        "text" : body
    }
    print("Data is: ")
    pprint(data)
    return(data)

def mailGun():
    data = createMail()
    if(data == False):
        print("Unable to send mail. Unable to obtain mail address")
        return("Unable to send mail. Unable to obtain mail address")
    response = sendMail(data)
    return(response)