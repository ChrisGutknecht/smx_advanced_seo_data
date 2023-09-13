/* REPLACE `your_gcp_project` AND `analytics_your_property` to your settings */
/* REPLACE 'params.value.string_value' to your 404 title identifier */

with ga4_pageviews_404_live_overall as (

    select
        user_pseudo_id as user_id,
        timestamp_micros(event_timestamp) as dateTime_ga4, 
        event_name,
        params.value.string_value
    from  
        /* update this project.dataset.table reference */
        `your_gcp_project`.`analytics_your_property`.`events_intraday_*`,
        unnest(event_params) as params 
    where 
        parse_date('%Y%m%d', regexp_extract(_table_suffix,'[0-9]+')) = current_date()
        /* query last 120 minutes*/
        and timestamp_micros(event_timestamp) between
            timestamp_sub(current_timestamp(), interval 2 hour) 
            and current_timestamp()
        and event_name = 'page_view'
        and params.key = 'page_title'
        and params.value.string_value like '%404%'

)

select * from ga4_pageviews_404_live_overall