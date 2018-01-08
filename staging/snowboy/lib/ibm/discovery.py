import json, requests, re, nltk
from pprint import pprint
from .bingSpeech.speechToText import discoveryStt
from .bingSpeech.textToSpeech import tts
from watson_developer_cloud import DiscoveryV1
from .audioRecorderAutoStop import record_to_file

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

def getIBMCreds():
    credentials = json.load(open('../credentials.json'))
    ibmCreds = credentials['ibm']['discovery']
    return ibmCreds


# In[16]:


def getQuery():
    tts('Please state your query. ')
    record_to_file('discoveryQuery.wav')
    query = discoveryStt()
    return(query)

def getQuery2():
    query = input("Please tell me your query: \n")
    return(query)

# In[17]:


def constructQuery(query):
    query_options = {'natural_language_query': query,
                 'count' : 3,
                 'passages':True}
    return(query_options)


# In[18]:


def getQueryResults(discoveryDetails, queryOptions):
    env_id, collections, discovery = discoveryDetails
    queryResults = discovery.query(environment_id=env_id, 
                               collection_id=collections[0]['collection_id'],
                               natural_language_query=queryOptions['natural_language_query'], 
                               passages=queryOptions['passages'], count=queryOptions['count'])
    return(queryResults)


# In[19]:


def cleanPassage(passage):
    tagRegEx = re.compile('<.*?>')
    cleanedText = re.sub(tagRegEx, '', passage)
    cleanedText = cleanedText.rstrip()
    cleanedText = cleanedText.replace('\n', '. ')
    return(cleanedText)


# In[20]:


def getPassage(queryResults):
    passages = []
    for passage in queryResults['passages']:
        passages.append(passage)
    passageScore = 0
    targetPassages = []
    for passage in passages:
        pprint(passage)
        for key in passage.keys():
            if(passageScore < passage['passage_score']):
                passageScore = passage['passage_score']
                targetPassages.append(passage)
    if(len(targetPassages) == 0):
        print("Nothing found")
        return("Nothing found. Try again.")
    targetPassage = targetPassages[0]['passage_text']
    cleanedPassage = cleanPassage(targetPassage)
    print("Target passage with highest score is: ")
    print(targetPassage)
    return(cleanedPassage)


# In[21]:


def askDiscovery():
    print("Discovery service intiated")
    ibmCreds = getIBMCreds()
    discovery = DiscoveryV1(version='2017-11-07',
                            username=ibmCreds['username'],
                            password=ibmCreds['password'])
    env = discovery.list_environments()['environments'][1]
    print("Environment Details:\n {}".format(env))
    env_id = env['environment_id']
    collections = discovery.list_collections(env_id)
    collections = collections['collections']
    print("Collection: \n{}".format(collections))
    discoveryDetails = (env_id, collections, discovery)
    query = getQuery()
    if(query[0] == False):
        return(query[1])
    print("Unformatted query is: {}".format(query[1]))
    query = removePunc(query[1])
    print("Formatted query is: {}".format(query[1]))
    queryOptions = constructQuery(query)
    print("Query options are: {}".format(queryOptions))
    queryResults = getQueryResults(discoveryDetails, queryOptions)
    print("Query results: {}".format(queryResults))
    passage = getPassage(queryResults)
    print("Passage after cleaning is: ")
    print("--------------------***--------------------")
    print(passage)
    return(passage)

def askDiscovery2():
    print("Discovery service intiated")
    ibmCreds = getIBMCreds()
    discovery = DiscoveryV1(version='2017-11-07',
                            username=ibmCreds['username'],
                            password=ibmCreds['password'])
    env = discovery.list_environments()['environments'][1]
    print("Environment Details:\n {}".format(env))
    env_id = env['environment_id']
    collections = discovery.list_collections(env_id)
    collections = collections['collections']
    print("Collection: \n{}".format(collections))
    discoveryDetails = (env_id, collections, discovery)
#     query = getQuery()
    query = getQuery2()
#     print("Unformatted query is: {}".format(query[1]))
#     query = removePunc(query[1])
#     print("Formatted query is: {}".format(query[1]))
    queryOptions = constructQuery(query)
    print("Query options are: {}".format(queryOptions))
    queryResults = getQueryResults(discoveryDetails, queryOptions)
    print("Query results: {}".format(queryResults))
    passage = getPassage(queryResults)
    print("--------------------***--------------------")
    print("Passage after cleaning is: ")
    print("--------------------***--------------------")
    print(passage)
    return(passage)