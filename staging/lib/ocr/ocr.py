
# coding: utf-8

# # Handwritten OCR
# 
# Here, we first use OCR to get text data from the images. Following which, we store that data in a repo that allows for querying and retrieving.

# In[91]:


from pymongo import MongoClient
import json, requests, time
# import pandas as pd
from pprint import pprint


# # Helper Functions

# ### CV API Details:

# In[33]:


def getCVCreds():
    credentials = json.load(open('../credentials.json'))
    cvCreds = credentials['cognitiveServices']['computerVision']
    return cvCreds


# In[80]:


def getCVRequestURL(cvCreds):
    fullEndpoint = cvCreds['endPoint'] + "/RecognizeText"
    return(fullEndpoint)


# In[81]:


def getCVOperationsURL(cvCreds):
    fullEndPoint = cvCreds['endPoint'] + "/textOperations"
    return(fullEndPoint)


# In[35]:


def getCVKey(cvCreds):
    return cvCreds['key']


# In[36]:


def createHeaders(subscription_key):
    headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': subscription_key,
    }
    return(headers)


# In[37]:


def createParams():
    params = {
        "handwriting" : 'true'
    }
    return params


# In[73]:


def getOperationsID(headers, cvCreds):
    getCVOperationsURL(cvCreds)
    operationsID = operationsLocation.split('https://eastus2.api.cognitive.microsoft.com/vision/v1.0/textOperations')[1]
    operationsID = operationsID.replace("/","")
    return(operationsID)


# In[116]:


def generateOCRRequest():
    cvCreds = getCVCreds()
    endpoint = getCVRequestURL(cvCreds=cvCreds)
    key = getCVKey(cvCreds)
    headers = createHeaders(key)
    params = createParams()
    body = open('./sample.png','rb')
    response = requests.post(url=endpoint, headers=headers, params=params, data=body)
    body.close()
    response.close()
    return(response,headers)


# In[113]:


def handleResponse(res,headers):
    if(res.status_code != 202):
        pprint("Error: " + res.status_code)
        pprint("Error: " + res.reason)
        return(res.reason)
    else:
        pprint("OCR submitted for analysis, stand by. This may take up to ten seconds")
        time.sleep(5)
        operationsLocation = res.headers['Operation-Location']
        analyzedText = checkStatus(operationsLocation,headers)
        return(analyzedText)


# In[114]:


def checkStatus(operationsLocation, headers):
    failed = "Polling failed. Please try again"
    req = requests.get(url=operationsLocation, headers=headers)
    if(req.status_code == 200):
        pprint("Analysis complete")
        req.close()
        return({
            "status" : True,
            "text" : req.json()
        })
    else:
        flag = False
        req.close()
        retries = 5
        count = 0
        while(Flag != True):
            time.sleep(1)
            req = requests.get(url=operationsLocation, headers=headers)
            req.close()
            if(req.status_code == 200):
                flag = True
                pprint("Analysis complete after polling")
                return({
                    "status" : True,
                    "text" : req.json()
                })
            count = count + 1
            if(count>=retries):
                flag = True
                return({
                    "status" : False,
                    "text" : req.reason
                })
        return("Something went wrong")


# In[1]:


def captureImage():
#     NOTE: FILE NAME IS HARDCODED
#     Save as "sample.*"  
    pprint("Image captured!")


# In[176]:


def getRecognizedText():
    captureImage()
    res,headers = generateOCRRequest()
    jsonText = handleResponse(res,headers)
    recogResult = jsonText['text']['recognitionResult']['lines']
    valueList = []
    for line in recogResult:
        valueList.append(line['text'])
    return(valueList)

