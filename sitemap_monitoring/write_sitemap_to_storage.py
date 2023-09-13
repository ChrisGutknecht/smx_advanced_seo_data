import pandas as pd
import os
import json
from datetime import datetime
from google.cloud import bigquery
from dateutil.parser import parse
from advertools import sitemap_to_df

# Set your GCP project id here
project_id = 'project_id'

# Adapt this table schema if needed
table_schema = [
    {'name': 'date', 'type': 'DATE'},
    {'name': 'url', 'type': 'STRING'},
    {'name': 'lastmod_date', 'type': 'DATE'},
    {'name': 'changefreq', 'type': 'STRING'},
    {'name': 'priority', 'type': 'FLOAT'},
    {'name': 'sitemap_url', 'type': 'STRING'},
    {'name': 'image_url_first', 'type': 'STRING'}
]


def save_sitemap_to_storage(request):
    """
    Entry method to entire logic of parsing request object, fetching sitemap and storage write

    Parameters
    ----------
    request : object
        A flask request object containing the parameters project id, table name, bucket and file name

    Returns
    -------
    response_header : tuple
        A flask response header for the invoked cloud function
    """

    # Parsing the request object for the upload parameters
    request = request.get_data()
    try: 
        request_json = json.loads(request.decode())
        print(request_json)
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return ("JSON Error", 400)

    sitemap_url = request_json.get('sitemap_url')
    country_string = request_json.get('country_string')
    full_table_name = request_json.get('full_table_name')


    # Fetch the sitemap via advertools and convert to a dataframe
    sitemap_df = sitemap_to_df(sitemap_url)
    
    # column transformations
    sitemap_df['sitemap_name'] = sitemap_df.apply(lambda row: get_sitemap_name(row.sitemap, country_string), axis=1)
    date_today = datetime.strftime(datetime.now(), '%Y-%m-%d')
    sitemap_df.insert(0, 'date', date_today)
    sitemap_df['lastmod'] = sitemap_df.apply(lambda row: datetime.strftime(parse(str(row.lastmod).replace('NaT', str(date_today))), "%Y-%m-%d"), axis=1)
    sitemap_df['image_loc'] = sitemap_df['image_loc'].fillna('')
    
    # static value to avoid datatype errors
    sitemap_df['priority'] = 0.5
    sitemap_df['changefreq'] = 'daily'

    # column dropping and renaming
    sitemap_df.rename(columns={
            'loc':'url', 'sitemap':'sitemap_url', 
            'lastmod':'lastmod_date', 'image_loc':'image_url_first'
        }, inplace=True)

    required_columns = ['date', 'url', 'lastmod_date', 'changefreq', 'priority', 'sitemap_url', 'image_url_first']

    sitemap_df = sitemap_df[required_columns]

    # Write data to BigQuery
    pandas_gbq.to_gbq(sitemap_df, full_table_name, project_id=project_id, table_schema=table_schema, if_exists='append')

    return ('Sitemap saved to BigQuery',200)