## 1. How to set up the 404 live alerts table in BigQuery

* If not using a framework like dbt, create a view table with SQL code from the file <code>ga4_pageviews_404_live.sql</code> and simply name it <code>ga4_pageviews_404_live</code>.
* Query the new table with a <xode>select * </code> to make sure it runs correctly.

## 2. How to deploy this cloud function (via the UI)

* In your GCP project, navigate to cloud functions: <https://console.cloud.google.com/functions>
* Create a cloud function named <code>check_ga4_live_events</code>
* Choose <code>1st gen</code> as environment, <code>256 MB</code> for Memory and <code>540</code> as Timeout and leave all other default settings.
* Make sure your runtime service account has the necessary permissions or the see execution errors for instructions if any are missing.

## 3. How to set up a schedule for the cloud function
Next, navigate to Cloud scheduler to invoke this cloud function regularly: <https://console.cloud.google.com/cloudscheduler>.

For the scheduler job configuration:

* set the cron schedule to this example configuration: <code>0 7-23 * * *</code>
* Set **Target Type** to <code>HTTP</code>.
* Copy the cloud function **URL** from the trigger tab to the URL field
* Set the **HTTP method** to <code>POST</code>.
* In the **HTTP method** section section,set <code>Content-Type</code> to <code>application/json</code>
* the **Body** represents this <code>POST</code> payload and should look like this. Set your parameters to your preferences and iterate to the right levels if necessary.
```
 {
    "time_frame_min" : 120,
    "max_event_threshold" : 70,
    "full_table_name" : "your_project.your_dataset.alerts_ga4_pageviews_404_live",
    "message_title_prefix" : "GA4 LiveAlerts | 404 Page View Alert for last ",
    "message_text_prefix" : "High 404 Events! More details at https://lookerstudio.google.com/s/YOUR_REPORT_URL |  Event count found : "
} 
```
* Retry settings are optional and not necessary