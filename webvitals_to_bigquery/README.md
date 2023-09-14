## 1. How to set up the webvitals events table in BigQuery

* Create an empty, date partitioned table by column <code>date</code> and name it according to your country sitemap, for instance <code>pagespeed_api_metrics</code>.
* Use the following schema in the text editor: 
```
date:DATE,
country:STRING,
domain:STRING,
url_type:STRING,
url:STRING,
url_final:STRING,
overall_category:STRING,
largest_contentful_paint_s:FLOAT,
first_meaningful_paint_s:FLOAT,
first_input_delay:FLOAT,
cumulative_layout_shift_s:FLOAT,
first_contentful_paint_s:FLOAT,
time_to_interactive_s:FLOAT,
total_blocking_time_s:FLOAT,
speed_index_s:FLOAT,
observed_dom_content_loaded_s:FLOAT,
observed_first_visual_change_s:FLOAT,
observed_last_visual_change_s:FLOAT,
interaction_to_next_paint:STRING,
time_to_first_byte:STRING,
_loaded_at:DATETIME,
performance_score:INTEGER
```

## 2. How to deploy this cloud function (via the UI)

* In your GCP project, navigate to cloud functions: <https://console.cloud.google.com/functions>
* Create a cloud function with <code>2nd gen</code> as environment
* Set the **Function name** <code> write-pagespeed-metrics-to-storage</code> and a region close to your location
* For easier setup, set **Authentication** to <code>Allow unauthenticated invocations</code>. This allows for a simpler setup with less configuration. Since this cloud function only queries data, it is not as sensitive.
* Set <code>2 GiB</code> for Memory and <code>3600</code> seconds as Timeout, this equates to 60minutes. Leave all other default settings.
* Make sure your runtime service account has the necessary permissions or the see execution errors for instructions if any are missing.

* In the code section, set the **Runtime** to <code>Python 3.11</code> (September 2023).
* Set the **Entry point** to <code>save_pagespeed_metrics</code>.
* Add the Python code from the file <code>write_webvitals_to_storage.py</code> to the file <code>main.py</code>.
* In the <code>requirements.txt</code>, add the following packages. These will be installed via the pip package manager.
```
google-cloud-bigquery
pandas
pandas-gbq
datetime
```
* Hit the deploy button as final setup. To test the cloud function, you need a <code>POST</code> payload, see the scheduler section below.

## 3. How to set up a schedule for the cloud function
Navigate to Cloud scheduler to invoke this cloud function regularly: <https://console.cloud.google.com/cloudscheduler>.

For the scheduler job configuration:

* set the **Name** to <code>write_pagespeed_metrics_to_storage</code> or your preferred value.
* set the cron schedule to this example configuration: <code>0 10,14,18,22 * * *</code>. This will fetch **four** times a day.
* Set **Target Type** to <code>HTTP</code>.
* Copy the cloud function **URL** from the trigger tab to the URL field
* Set the **HTTP method** to <code>GET</code>.
* Retry settings are optional
* Test your scheduler and cloud function setup by executing a force run of the scheduler.

## 4. How to set up MS Teams alerts for changes in business metrics? (ADVANCED)

- This implementation is based on Google Cloud, BigQuery and the dbt framework
- For an introduction to the dbt framework, see here: https://www.getdbt.com/blog/what-exactly-is-dbt/
- To get startetd with *dbt cloud* (recommended for beginners), see here: https://docs.getdbt.com/docs/get-started/dbt-cloud-features

### 4.1 Set up your dbt tests

- When building your models in dbt, you can set up tests for these model and their columns: https://docs.getdbt.com/docs/build/tests
- You can run these tests daily with the <code>dbt test</code> or <code>dbt run</code> to execute these tests, either in dbt cloud or in a custom cloud Python runtime like Apache Airflow or Google Cloud Run
- To create test summaries of multiple tests and send them MS Teams, you need to run a dbt macro called <code>{{ store_test_results() }}</code>. This macro needs to be added to the <code>on-run-end</code> operation in your <code>dbt_project.yml</code> file. See also this tutorial: https://www.getdbt.com/blog/dbt-live-apac-tracking-dbt-test-success
```
on-run-end: 
  - “{{ store_test_results(results) }}”
```
- When these test results are stored in BigQuery, use a **Create Sink** for updates on this table via the **Logs Explorer** UI: https://console.cloud.google.com/logs/query
- In the **Logs Router Sink**, create a new sink with <code>Cloud Pub/Sub Topic</code> as a **Sink destination**.
- This PubSub topic should trigger a **cloud function** which then queries the dbt test result table. 
- The cloud function code is can be shared upon request. It maps the test results from a specific dbt job to a Teams channel, converts the SQL result to a dataframe and displays it via <code>to_html()</code> and adds a couple of HTML elements via the <code>pymsteams</code> Python package.