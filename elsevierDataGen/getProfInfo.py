"""An example program that uses the elsapy module"""

from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json
import pandas as pd
from pprint import pprint
from subject import Subject
from professor import Professor
    
## API configuration and client setup
con_file = open("config.json")
config = json.load(con_file)
con_file.close()
client = ElsClient(config['apikey'])

all_subject_data = {} #map from subject ID as a str to a subject object
all_prof_info = []

#Collect our prof author IDs
prof_df = pd.read_csv("../webscrapers/professors.csv")
prof_ids = []
for name in prof_df['Name'][0:1]: 
    ## Initialize author search object and execute search
    print(name.split(' ')[0])
    print(name.split(' ')[1])
    
    auth_srch = ElsSearch('authlast(' + name.split(' ')[1] + ') and authfirst(' + name.split(' ')[0] + ') and affil(Yale)','author')
    auth_srch.execute(client)
    print (name + "auth_srch has", len(auth_srch.results), "results.")
    print(auth_srch.results[0]['dc:identifier'].split(':')[1])
    prof_ids.append(auth_srch.results[0]['dc:identifier'].split(':')[1])
    
    #Process prof IDs: get their subjects and corresponding publication frequencies
    prof = ElsAuthor(
            uri = 'https://api.elsevier.com/content/author/author_id/' + str(prof_ids[0]))
    # Read author data, then write to disk
    if prof.read(client):
        #pprint(prof.data)
        #print(prof.data['subject-areas']['subject-area'])
        #print(prof.data['author-profile']['classificationgroup']['classifications']['classification'])#get subject names   
        #associated subject-publication frequency table w/ professor 
        subject_to_freq = {}
        for subject_freq in prof.data['author-profile']['classificationgroup']['classifications']['classification']:
            subject_to_freq[subject_freq['$']] = subject_freq['@frequency']
        tot_citations = prof.data['coredata']['document-count']
        all_prof_info.append(Professor(name, prof_ids[-1], tot_citations, subject_to_freq))
        #update our subject list
        for subject in prof.data['subject-areas']['subject-area']:
            if subject['@code'] not in all_subject_data:
                all_subject_data[subject['@code']] = Subject(subject['$'],subject['@abbrev'],subject['@code'])
        prof.write()
    else:
        print ("Read author failed.")