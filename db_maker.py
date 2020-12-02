'''
Part 2: DB and Query
pip install pandas
'''

import ast
import csv
import sqlite3
import pandas as pd

def create_tables(conn):
    '''Drops and creates sqlite tables'''
    
    c = conn.cursor()

    c.execute('''DROP TABLE if exists publications;''')
    c.execute('''CREATE TABLE publications
                (PMID integer, Abstract text, Title text, Pub_Date text,
                PRIMARY KEY (PMID))''')

    c.execute('''DROP TABLE if exists authors;''')
    c.execute('''CREATE TABLE authors
                (AID integer, PMID integer, Full_Name text, Last_Name text, First_Name text,
                PRIMARY KEY (AID))''')
    c.execute('''CREATE INDEX idx_author_name ON authors (PMID);''')
    conn.commit()
    return 'Created tables'

def load_file(conn, pub_df):
    '''
    conn: connection to database
    pub_df: pandas dataframe from the pub_crawler.py csv
    Modifies the dataframe and prepares it load into the
    tables authors and publications
    '''

    #converts strings of the authors to a list
    pub_df['Authors'] = pub_df['Authors'].apply(lambda x: ast.literal_eval(x))
    pub_df['Pub_Date'] = pd.to_datetime(pub_df['Pub_Date'], yearfirst=True)

    #creates a row for each author for each pmid
    author_df = pub_df[['PMID','Authors']].explode('Authors')
    author_df = author_df.reset_index(drop=True)
    #separates the authors name into two columns, 
    name_df = author_df['Authors'].str.split(',', 1).apply(pd.Series)
    author_df = pd.concat([author_df, name_df], axis=1)
    author_df = author_df.reset_index()
    author_df = author_df.rename(columns={0:'Last_Name', 1:'First_Name', 
                                          'Authors':'Full_Name','index':'AID'})
    author_df['First_Name']= author_df['First_Name'].str.strip()
    author_df['Last_Name']= author_df['Last_Name'].str.strip()
    pub_columns= ['PMID','Pub_Date','Abstract','Title']

    #imports the data into the tables created
    author_df.to_sql('authors', conn, index=False, if_exists='append')
    pub_df[pub_columns].to_sql('publications', conn, index=False, if_exists='append')
    return 'Data Loaded'

def author_query(conn, first_name, last_name):
    c = conn.cursor()
    c.execute('''
    SELECT pubs.PMID, pubs.Abstract, pubs.Title, 
           pubs.Pub_Date, auth.AID, auth.Full_Name
    FROM publications pubs inner join authors auth on auth.PMID = pubs.PMID 
    WHERE Last_Name like ? and First_Name like ?;
    ''', (last_name+'%', first_name+'%'))
    return c.fetchall()

def author_search_prompt():

    first_name = input("Enter first name of author you would like to search: ")
    last_name = input('Enter last name of author you would like to search: ')
    
    if len(first_name) == 0 and len(last_name) == 0:
        raise Exception("A first or last name must be submitted")
    elif len(first_name) == 0:
        print("WARNING: This will search for all authors with last name {}".format(last_name))
    elif len(last_name) == 0:
        print("WARNING: This will search for all authors with first name {}".format(first_name))

    return {'first_name':first_name, 'last_name':last_name}


if __name__ == "__main__":

    conn = sqlite3.connect("publications.db")
    create_tables(conn)
    
    pub_df = pd.read_csv('publication_output.csv')
    load_file(conn, pub_df)

    author_search_dict = author_search_prompt()
    output_data = author_query(conn, author_search_dict['first_name'],author_search_dict['last_name'])
    
    for i in output_data:
        print(i[2])
    conn.close()
