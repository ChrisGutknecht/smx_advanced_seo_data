

https://console.cloud.google.com/vertex-ai/workbench


## 1. How to set up the sitemap table in BigQuery

*  Create a an empty, date partitioned table and name it according to your country sitemap, for instance <code>sitemap_de_daily</code>.
* Use the following schema in the text editor: 
```
date: DATE,
url: STRING,
lastmod_date: DATE,
changefreq: STRING,
priority: FLOAT,
sitemap_url: STRING,
image_url_first: STRING
```

## 2. How to set up a Vertex AI managed notebook instance (via the UI)

* In your GCP project, navigate to Vertex AI workbench : <https://console.cloud.google.com/vertex-ai/workbench>
* Create a managed instance
* Set the **Function name** <code>check_ga4_live_events</code> and a region close to your location
* For easier setup, set **Authentication** to <code>Allow unauthenticated invocations</code>. This allows for a simpler setup with less configuration. Since this cloud function only queries data, it is not as sensitive.
* Set <code>256 MB</code> for Memory and <code>540</code> as Timeout and leave all other default settings.
* Make sure your runtime service account has the necessary permissions or the see execution errors for instructions if any are missing.

* In the code section, set the **Runtime** to <code>Python 3.11</code> (September 2023).
* Set the **Entry point** to <code>save_sitemap_to_storage</code>. This cloud function can be reused for different sitemaps by adding different sitemap URLs and pointing to different table names, although multiple sitemaps could be written into the same table.
* Add the Python code from the file <code>write_sitemap_to_storage.py</code> to the file <code>main.py</code>.
* In the <code>requirements.txt</code>, add the following packages. These will be installed via the pip package manager.
```
pandas-gbq
advertools
python-dateutil
pandas
DateTime
```
* Hit the deploy button as final setup. To test the cloud function, you need a <code>POST</code> payload, see the scheduler section below.

## 3. How to set up a schedule for the cloud function
Navigate to Cloud scheduler to invoke this cloud function regularly: <https://console.cloud.google.com/cloudscheduler>.

For the scheduler job configuration:

* set the **Name** to <code>save_sitemap_to_storage</code> or your preferred value.
* set the cron schedule to this example configuration: <code>0 5 * * *</code>. This will fetch at 5 am.
* Set **Target Type** to <code>HTTP</code>.
* Copy the cloud function **URL** from the trigger tab to the URL field
* Set the **HTTP method** to <code>POST</code>.
* In the **HTTP method** section section,set <code>Content-Type</code> to <code>application/json</code>
* the **Body** represents this <code>POST</code> payload and should look like this. Set your full table name to your preferences.
```
{
    "sitemap_url" : "https://www.website.de/sitemap_index.xml",
    "full_table" : "your_project.your_dataset.sitemap_de_daily"
}
```
* Retry settings are recommended if the sitemap is generated on request, then set **Max retry attempts** to <code>2</code>.
* Test your scheduler and cloud function setup by executing a force run of the scheduler.