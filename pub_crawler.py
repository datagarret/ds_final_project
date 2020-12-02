'''
Part 1: Crawler
biopython needs to be installed on system user either
pip install biopython or conda install biopython

Below is a hyper link that gave a nice example of how to query by key term
http://biopython.org/DIST/docs/tutorial/Tutorial.html#sec158

This shows how to query by date
https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
'''

import re
import numpy as np
from Bio import Entrez, Medline
import csv


#Enter your email
Entrez.email = "garret.munoz@uth.tmc.edu"

def date_converter(input_date):
    '''
    input_date: string of date and must have format MM/DD/YYYY
    outputs a string with for the date in format YYYY/MM/DD
    This will not catch months that don't exist such as 13 etc.
    '''
    #Checks if it matches the needed date format
    
    match = re.match("[0-1][0-9]/[0-3][0-9]/[0-9]{4}", input_date)
    if match is not None:
        output_date = input_date.split('/')
        output_date = output_date[2] + '/' + output_date[0] + '/' + output_date[1]
    else:
        raise Exception("Date must be in format MM/DD/YYYY")
    
    if int(input_date[0:2]) > 12 or int(input_date[0:2]) < 1:
        raise Exception("Month must be between 1 and 12")

    if int(input_date[3:5]) > 31 or int(input_date[3:5]) < 1:
        raise Exception("Dates must be between 1 and 31") 
    return output_date

def pubmed_crawl(key_term, mindate, maxdate):
    '''
    searches publications based on a key term between the mindate and maxdate
    key_term: string value of the topic to be searched
    mindate: minimum date of publication in format of 'YYYY/MM/DD'
    maxdate: maximum date of publication in format of 'YYYY/MM/DD'
    
    TODO: Notice mindate and maxdate utilize a different date format than given by
    the specifications (MM/DD/YYYY), we will need to clean the inputted date to the format that
    Entrez requires (YYYY/MM/DD). We should also have a check that the length of the inputted dates
    are equal to 10
    '''

    #mindate must be less than or equal to the maxdate
    assert (maxdate>=mindate), 'End date must be after or on start date'

    #queries for the ID by key term
    handle = Entrez.esearch(db="pubmed", term=key_term, retmax=100000,datetype='edat' ,mindate=mindate, maxdate=maxdate)
    record = Entrez.read(handle)
    idlist = record['IdList']
    handle.close()
    
    article_count = len(idlist)

    #retrieves publication data by the id's
    records = []
    retstart_list = [x for x in range(0, article_count, 1000)]
    for retstart in retstart_list:
        handle = Entrez.efetch(db="pubmed", id=idlist, 
        rettype="medline", retmode="text", 
        retstart=retstart, retmax=1000)
        txt_output = Medline.parse(handle)
        for record in txt_output:
            records.append(record)
        handle.close()
    return records

#TODO Parse the PMID, authors, abstract, and publication time from the outputted data
# and then export results to csv

def pubmed_parser(input_record):

    pmid =  int(input_record['PMID'])
    try:
        title = input_record['TI']
    except KeyError:
        #there are some articles that have no abstract
        return None
    try:
        abstract = input_record['AB']
    except KeyError:
        #there are some articles that have no abstract
        abstract = ''
    try:
        pub_date = input_record['EDAT'][0:10]
    except KeyError:
        return None
    try:
        authors = input_record['FAU']
    except KeyError:
        return None

    output_record = {'PMID': pmid, 'Authors':authors,
                     'Pub_Date': pub_date, 'Abstract':abstract,
                     'Title':title}

    return output_record

#test def
def hiv_crawl_test():
    key_word = 'HIV'
    min_date = '01/01/2020'
    max_date = '03/01/2020'

    min_date = date_converter(min_date)
    max_date = date_converter(max_date)

    pub_data = pubmed_crawl(key_word, min_date, max_date)

    return pub_data

def data_outputter(pub_data):
    output_pub_data = []
    for record in pub_data:
        parsed_record = pubmed_parser(record)
        if parsed_record is not None:
            output_pub_data.append(parsed_record)
    return output_pub_data

def pub_prompt(file_name):

    assert (file_name.endswith('csv')), 'file_name must be a .csv file'

    key_word = input('Key Word to search: ')
    assert (len(key_word) > 0), 'A key word must be used'
    
    min_date = input('Start date (MM/DD/YYYY): ')
    max_date = input('End date (MM/DD/YYYY): ')
    min_date = date_converter(min_date)
    max_date = date_converter(max_date)
    
    pub_data = pubmed_crawl(key_word, min_date, max_date)
    output_pub_data = data_outputter(pub_data)

    with open(file_name, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_pub_data[0].keys())
        writer.writeheader()
        writer.writerows(output_pub_data)
    
    print('query outputted {} publications'.format(len(output_pub_data)))
    print('file written to {}'.format(file_name))
    return True

if __name__ == "__main__":
    pub_prompt('publication_output.csv')





