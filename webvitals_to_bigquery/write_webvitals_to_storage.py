# Import required packages 
import json
import requests
import pandas_gbq
import pandas as pd
import time
import urllib
from urllib.parse import urlencode
from datetime import date, datetime
import os

from google.cloud import storage
from google.cloud import bigquery

project_id = 'your_project_id'
dataset_name = 'your_dataset'
table_name = 'pagespeed_api_metrics'
full_table_name = dataset_name + '.' + table_name

# set the country 
country = 'DE'

# Retrieve your pagespeed API key from the cloud console: 
# https://developers.google.com/speed/docs/insights/v5/get-started#APIKey
# You should reference private keys via secret manager, via adding the value as a secret
api_key = 'sdfsfsdfff'


table_schema = [
    {'name':'date', 'type':'DATE'},
    {'name':'country', 'type':'STRING'},
    {'name':'domain', 'type':'STRING'},
    {'name':'url_type', 'type':'STRING'},
    {'name':'url', 'type':'STRING'},
    {'name':'url_final', 'type':'STRING'},
    {'name':'overall_category', 'type':'STRING'},
    {'name':'largest_contentful_paint_s', 'type':'FLOAT'},
    {'name':'first_meaningful_paint_s', 'type':'FLOAT'},
    {'name':'first_input_delay', 'type':'FLOAT'},
    {'name':'cumulative_layout_shift_s', 'type':'FLOAT'},
    {'name':'first_contentful_paint_s', 'type':'FLOAT'},
    {'name':'time_to_interactive_s', 'type':'FLOAT'},
    {'name':'total_blocking_time_s', 'type':'FLOAT'},
    {'name':'speed_index_s', 'type':'FLOAT'},
    {'name':'observed_dom_content_loaded_s', 'type':'FLOAT'},
    {'name':'observed_first_visual_change_s', 'type':'FLOAT'},
    {'name':'observed_last_visual_change_s', 'type':'FLOAT'},
    {'name':'interaction_to_next_paint', 'type':'STRING'},
    {'name':'time_to_first_byte', 'type':'STRING'},
    {'name':'_loaded_at', 'type':'DATETIME'},
    {'name':'performance_score', 'type':'INTEGER'}
]


# List of URLS: Change the URL set and sections to your liking
# The only limitation is the 60min runtime of the cloud function

own_urls = {
    'List' : [
        'https://www.bergzeit.de/ausruestung/',
        'https://www.bergzeit.de/ausruestung/skitourenausruestung/tourenski/',
          ],
    'Magazin': [
        'https://www.bergzeit.de/magazin/',
        'https://www.bergzeit.de/magazin/beste-tourenski-testsieger/'
    ],
    'Marke' : [
        'https://www.bergzeit.de/marken/arcteryx/',
        'https://www.bergzeit.de/marken/cmp/'
    ],
    'Produktdetail' : [
        'https://www.bergzeit.de/p/arcteryx-mens-beta-lt-jacket/1090496/',
        'https://www.bergzeit.de/p/bergzeit-last-minute-gutschein-zum-selbstdrucken/7000077/',
    ],
    'Start' : ['https://www.bergzeit.de/'],
    'Suche' : [
        'https://www.bergzeit.de/search/?query=handschuhe+kinder',
        'https://www.bergzeit.de/search/?query=karabiner'
    ]
}

comp_urls = {
    'Start' : 'https://www.bergfreunde.de/',
    'List' : 'https://www.bergfreunde.de/kletterschuhe/',
    'Marke' : 'https://www.bergfreunde.de/marken/petzl/',
    'Suche' : 'https://www.bergfreunde.de/s/petzl/?searchparam=petzl',
    'Magazin' : 'https://www.bergfreunde.de/blog/kaufberatung-fahrradpacktaschen/',
    'Produktdetail' : 'https://www.bergfreunde.de/petzl-hirundos-klettergurt/'
}

comp_urls_2 = {
    'Start' : 'https://www.decathlon.de',
    'List' : 'https://www.decathlon.de/sport/c0-alle-sportarten-a-z/c1-bergsteigen/_/N-1lnjag4',
    'Marke' : 'https://www.decathlon.de/browse/b/black-diamond/_/N-47cvry',
    'Suche' : 'https://www.decathlon.de/search?Ntt=petzl+tikka',
    'Magazin' : 'https://einblicke.decathlon.de/blog/second-use/',
    'Produktdetail' : 'https://www.decathlon.de/p/sup-board-stand-up-paddle-aufblasbar-x100-touring-einsteiger-11/_/R-p-303064?mc=8511826&c=BLAU'
}

comp_urls_3 = {
    'Start' : 'https://www.zalando.de/',
    'List' : 'https://www.zalando.de/damenbekleidung-shirts/',
    'Marke' : 'https://www.zalando.de/entdecken/levis-damen/',
    'Suche' : 'https://www.zalando.de/damen/?q=levis+501',
    'Magazin' : 'https://www.zalando-lounge.de/magazine/party-outfit-winter/#/',
    'Produktdetail' : 'https://www.zalando.de/levis-plus-graphic-way-back-tee-langarmshirt-black-l0m21d02s-q11.html'
}


def save_pagespeed_metrics(request): 

    # Create a dataframe from url list
    df_list = []
    
    own_urls_sorted = []
    for key, value in own_urls.items():
        
        # Iterate through BZ every list, get key and all URLs
        url_list = value
        for url in url_list:
            own_urls_sorted.append({'url_type': key, 'url': url})
            
    own_df = pd.DataFrame.from_dict(own_urls_sorted)
    own_df.insert(0, 'domain', 'https://www.bergzeit.de')

    comp_df = pd.DataFrame(comp_urls.items(), columns=['url_type', 'url'])
    comp_df.insert(0, 'domain', 'https://www.bergfreunde.de/')

    comp_df_2 = pd.DataFrame(comp_urls_2.items(), columns=['url_type', 'url'])
    comp_df_2.insert(0, 'domain', 'https://www.decathlon.de')

    comp_df_3 = pd.DataFrame(comp_urls_3.items(), columns=['url_type', 'url'])
    comp_df_3.insert(0, 'domain', 'https://www.zalando.de')

    full_df = pd.concat([own_df, comp_df, comp_df_2, comp_df_3])  

    response = {}

    # Iterate through the df
    for x in range(0, len(full_df)):

        # Define request parameter
        url = full_df.iloc[x]['url']

        # Insert returned json response into response
        response_url = get_api_json_response(url)

        if response_url: 
            response[url] = response_url
            
        time.sleep(1)

    # Create empty dataframe
    columns = [
        'url',
        'url_final',
        'overall_category',
        'largest_contentful_paint_s',
        'first_meaningful_paint_s',
        'first_input_delay',
        'cumulative_layout_shift_s',
        'first_contentful_paint_s',
        'time_to_interactive_s',
        'total_blocking_time_s',
        'speed_index_s',
        'observed_dom_content_loaded_s',
        'observed_first_visual_change_s',
        'observed_last_visual_change_s',
        'interaction_to_next_paint',
        'time_to_first_byte',
        'performance_score'
    ]
    df = pd.DataFrame(columns=columns)

    for (url, x) in zip(response.keys(), range(0, len(response))):

        try:
            # URL
            df.loc[x, 'url']  = url
            df.loc[x, 'url_final'] = response[url].get('lighthouseResult').get('finalUrl')
            df.loc[x, 'overall_category'] = response[url].get('loadingExperience').get('overall_category')

            # Fetching from audit metrics dictionary
            audit_metrics = response[url].get('lighthouseResult').get('audits').get('metrics').get('details').get('items')[0]
            loading_experience_metrics = response[url].get('loadingExperience').get('metrics')

            df.loc[x, 'largest_contentful_paint_s'] = audit_metrics.get('largestContentfulPaint')/1000
            df.loc[x, 'first_meaningful_paint_s'] = audit_metrics.get('firstMeaningfulPaint')/1000
            df.loc[x, 'first_contentful_paint_s'] = audit_metrics.get('firstContentfulPaint')/1000
            df.loc[x, 'first_input_delay'] = audit_metrics.get('maxPotentialFID')/1000
            df.loc[x, 'cumulative_layout_shift_s'] = audit_metrics.get('cumulativeLayoutShift')
            df.loc[x, 'time_to_interactive_s'] = audit_metrics.get('interactive')/1000 
            df.loc[x, 'total_blocking_time_s'] = audit_metrics.get('totalBlockingTime')/1000
            df.loc[x, 'speed_index_s'] = audit_metrics.get('speedIndex')/1000

            df.loc[x, 'observed_dom_content_loaded_s'] = audit_metrics.get('observedDomContentLoaded')/1000 
            df.loc[x, 'observed_first_visual_change_s'] = audit_metrics.get('observedFirstVisualChange')/1000 
            df.loc[x, 'observed_last_visual_change_s'] = audit_metrics.get('observedLastVisualChange')/1000 
            df.loc[x, 'performance_score'] = response[url].get('lighthouseResult').get('categories').get('performance').get('score')*100
        
        except BaseException as e:
            print(str(e))

        try:
            df.loc[x, 'interaction_to_next_paint'] = loading_experience_metrics.get('EXPERIMENTAL_INTERACTION_TO_NEXT_PAINT').get('category')
        except BaseException as e:
            print(str(e))

        try:      
            df.loc[x, 'time_to_first_byte'] = loading_experience_metrics.get('EXPERIMENTAL_TIME_TO_FIRST_BYTE').get('category')
        except BaseException as e:
            print(str(e))

    
    date_time = datetime.now()
    # add time stamp to allow multiple loads per day
    df.insert(0, '_loaded_at', date_time)
    df.insert(1, 'date', date_time.strftime('%Y-%m-%d'))
    df.insert(2, 'country', country)

    df_merged = pd.merge(df, full_df, on='url', how='left')
    print(df_merged.info())
    
    save_df_to_storage(df_merged)

    return ('data written to storage', 200)


def get_api_json_response(url):

    # API request url
    endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?'
    # Optional:  '&filter_third_party_resources=true'
    api_url = endpoint + 'url=' + urllib.parse.quote(url) +'&strategy=mobile' + '&key=' + api_key
    result = requests.get(api_url).content
    result_json = json.loads(result)
    
    return result_json


def save_df_to_storage(df):
    """
    Write the dataframe to BigQuery 

    Parameters
    ----------
    df : list
        the product attribut dataframe

    Returns
    -------
    None
    """

    # Write data to BigQuery
    pandas_gbq.to_gbq(df, full_table_name, project_id=project_id, table_schema=table_schema, progress_bar=True, if_exists='append')


# Not needed in this implementation, just as an alternative
def save_df_to_object_storage(df, file_name):
    """
    Write the dataframe to Cloud Storage 

    Parameters
    ----------
    df : list
        the product dataframe
    file_name : object
        the name of the file as found in the SFTP directoy

    Returns
    -------
    None
    """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket('seo_data_misc')
    blob = bucket.blob(file_name)
    df.to_csv('/home/{}'.format(file_name), index=False, sep='\t', doublequote=True, encoding='utf-8-sig')
    blob.upload_from_filename('/home/{}'.format(file_name))
    print('Feed uploaded')