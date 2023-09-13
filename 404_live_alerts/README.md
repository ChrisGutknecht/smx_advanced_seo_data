# How to deploy this cloud function via the UI

* In your GCP project, navigate to cloud functions: <https://console.cloud.google.com/functions>


Next, navigate to Cloud scheduler to invoke this cloud function regularly: <https://console.cloud.google.com/cloudscheduler>. 

For the scheduler job configuration:

* set the cron schedule to this example configuration:
```
0 7-23 * * *
```
* Set **Target Type** to <code>HTTP</code>.
* Copy the cloud function **URL** from the trigger tab to the URL field
* Set the **HTTP method** to <code>POST</code>.
* In the **HTTP method** section section,
    set <code>Content-Type</code> to
    and 


## When does the job run and how?

The [daily cloud scheduler job in the "adsdataprediction" project](https://console.cloud.google.com/cloudscheduler/jobs/edit/europe-west1/get_awin_orders?project=adsdataprediction) triggers [a cloud function](https://console.cloud.google.com/functions/details/europe-west3/get_awin_orders?env=gen1&project=adsdataprediction) to store all Awin orders to Cloud Storage in one csv file per country.

### How does the data land in BigQuery?

TBD...The output dataframes are [directly written to BigQuery](https://console.cloud.google.com/bigquery?project=bergzeit&ws=!1m9!1m4!4m3!1sbergzeit!2sdbt_sea_analytics!3sgads_ads_for_url_check!1m3!3m2!1sadsdataprediction!2sawin&d=awin&p=adsdataprediction&page=dataset) via the to_gbq method.
