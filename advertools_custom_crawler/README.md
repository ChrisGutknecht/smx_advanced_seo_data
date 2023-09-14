## 1. How to set up the seo crawl table in BigQuery

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
* Create a managed instance notebook.

* Leave most of the default settings until the Jupyter notebook UI opens.
* Set <code>100GB</code> for disk size, set the machine type according to the size of your website. For larger crawl of +50k URLs per website, we recommend a high-memory machine like <code>n1-highmem-16</code> which 104GB of memory. This is initially needed because advertools generated many columns in the crawl dataframe.
* As a service account, make sure the Vertex AI service account has the right permissions



## 3. How to set up a schedule for the notebook

* When the notebook is running and you're in the Jupyter UI, run a small test of max 100 URLs by setting <code>CLOSESPIDER_PAGECOUNT</code> to <code>100</code>.
* When this runs correctly, set a one-time execution in the Execute control panel. ONLY when this crawl runs correctly, set a weekly or regular schedule.