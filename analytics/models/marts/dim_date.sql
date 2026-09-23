{{ config(materialized='table') }}

with dates as (
    select match_date from {{ ref('stg_matches') }}
    union
    select match_date from {{ ref('stg_player_fixture') }}
),

distinct_dates as (
    select distinct match_date as full_date
    from dates
    where match_date is not null
)

select
    cast(strftime(full_date, '%Y%m%d') as integer)               as date_id,
    full_date,
    extract(year from full_date)                                 as year,
    extract(month from full_date)                                as month,
    strftime(full_date, '%B')                                    as month_name,
    strftime(full_date, '%A')                                    as day_of_week,
    case when extract(dow from full_date) in (0, 6) then true else false end as is_weekend
from distinct_dates
