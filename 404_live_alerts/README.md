## 1. How to set up the 404 live alerts table in BigQuery

* If not using a framework like dbt or Dataform, create a view table with the SQL code from the file <code>ga4_pageviews_404_live.sql</code> in this folder, and simply name it <code>ga4_pageviews_404_live</code>. The schema should be auto-created when you save the view table.
* Query the new table with a <code>select * </code> to make sure it runs correctly.

## 2. How to deploy this cloud function (via the UI)

* In your GCP project, navigate to cloud functions: <https://console.cloud.google.com/functions>
* Create a cloud function with <code>1st gen</code> as environment
* Set the **Function name** <code>check_ga4_live_events</code> and a region close to your location
* For easier setup, set **Authentication** to <code>Allow unauthenticated invocations</code>. This allows for a simpler setup with less configuration. Since this cloud function only queries data, it is not as sensitive.
* Set <code>256 MB</code> for Memory and <code>540</code> as Timeout and leave all other default settings.
* Make sure your runtime service account has the necessary permissions or the see execution errors for instructions if any are missing.

* In the code section, set the **Runtime** to <code>Python 3.11</code> (September 2023).
* Set the **Entry point** to <code>check_live_ga4_events</code>. This cloud function can be reused for different GA4 alerts like page view or transaction events by just pointing to different table names.
* Add the Python code from the file <code>get_404_live_events.py</code> to the file <code>main.py</code>.
* In the <code>requirements.txt</code>, add the following packages. These will be installed via the pip package manager.
```
google-cloud-storage
pandas
pandas-gbq
requests
pymsteams
```
* Hit the deploy button as final setup. To test the cloud function, you need a <code>POST</code> payload, see the scheduler section below.

## 3. How to set up a schedule for the cloud function
Navigate to Cloud scheduler to invoke this cloud function regularly: <https://console.cloud.google.com/cloudscheduler>.

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
* Test your scheduler and cloud function setup by executing a force run of the scheduler.