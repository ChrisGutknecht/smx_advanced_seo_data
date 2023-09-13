import requests
from datetime import datetime, date
import pandas as pd
import json
import os
from google.cloud import storage
import pymsteams

# set your teams webhook url here. Ask your admins how to set up or google it
webhook = 'https://company.webhook.office.com/webhookb2/13242343@213455/IncomingWebhook/12345/12345'

# Your GCP project_id
project_id = 'project_id'

def check_live_ga4_events(request):

    # Parsing the request object for the upload parameters
    request = request.get_data()
    try: 
        request_json = json.loads(request.decode())
        print(request_json)
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return ("JSON Error", 400)

    time_frame_min = request_json.get('time_frame_min')
    min_event_threshold = request_json.get('min_event_threshold')
    max_event_threshold = request_json.get('max_event_threshold')
    message_title = request_json.get('message_title_prefix')
    message_text = request_json.get('message_text_prefix')
    full_table_name = request_json.get('full_table_name')

    # Preparing the query
    query = 'select * from ' + full_table_name
    
    # Executing the query
    event_count = get_query_results(query)
    print('# of events' + str(event_count))
    event_threshold = min_event_threshold if min_event_threshold else max_event_threshold

    # Max 404 page view check
    if max_event_threshold:
        if event_count > max_event_threshold:
            send_simple_message(event_count, message_title, time_frame_min, message_text, event_threshold)

    # Min event check
    elif event_count < min_event_threshold: 
        send_simple_message(event_count, message_title, time_frame_min, message_text, event_threshold)

    return('Events in last ' + str(time_frame_min) + ' minutes : ' + str(event_count), '200')


def get_query_results(query):
    date = datetime.strftime(datetime.now(), '%Y%m%d')
    df = pd.io.gbq.read_gbq(query, project_id=project_id) 
    return df.shape[0]


def send_simple_message(count, message_title, time_frame_min, message_text, event_threshold):
    teams_message = pymsteams.connectorcard(webhook, verify=False)
    teams_message.title(message_title + str(time_frame_min) + ' minutes')
    teams_message.text(message_text + str(count) + '. Event threshold: ' + str(event_threshold))
    teams_message.send()