# How to set up the 404 live alerts table in BigQuery

* If not using a framework like dbt, create a view table with SQL code from the file <code>ga4_pageviews_404_live_overall.sql</code>

# How to deploy this cloud function via the UI

* In your GCP project, navigate to cloud functions: <https://console.cloud.google.com/functions>

Next, navigate to Cloud scheduler to invoke this cloud function regularly: <https://console.cloud.google.com/cloudscheduler>. 

For the scheduler job configuration:

* set the cron schedule to this example configuration: <code>0 7-23 * * *</code>
* Set **Target Type** to <code>HTTP</code>.
* Copy the cloud function **URL** from the trigger tab to the URL field
* Set the **HTTP method** to <code>POST</code>.
* In the **HTTP method** section section,set <code>Content-Type</code> to <code>application/json</code>
* the **Body** represents this <code>POST</code> payload and should look like this. M
```
 {
    "time_frame_min" : 120,
    "max_event_threshold" : 70,
    "table_name" : "alerts_ga4_pageviews_404_live_overall",
    "message_title_prefix" : "GA4 LiveAlerts | 404 Page View Alert in Overall for last ",
    "message_text_prefix" : "High 404 Events! More details at https://lookerstudio.google.com/s/YOUR_REPORT_URL |  Event count found : "
} 
```

## When does the job run and how?

The [daily cloud scheduler job in the "adsdataprediction" project](https://console.cloud.google.com/cloudscheduler/jobs/edit/europe-west1/get_awin_orders?project=adsdataprediction) triggers [a cloud function](https://console.cloud.google.com/functions/details/europe-west3/get_awin_orders?env=gen1&project=adsdataprediction) to store all Awin orders to Cloud Storage in one csv file per country.

### How does the data land in BigQuery?

TBD...The output dataframes are [directly written to BigQuery](https://console.cloud.google.com/bigquery?project=bergzeit&ws=!1m9!1m4!4m3!1sbergzeit!2sdbt_sea_analytics!3sgads_ads_for_url_check!1m3!3m2!1sadsdataprediction!2sawin&d=awin&p=adsdataprediction&page=dataset) via the to_gbq method.
