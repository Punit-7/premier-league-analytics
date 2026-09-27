{{ config(materialized='table') }}

-- A calendar spine: one row per day from the first match to the last scheduled
-- fixture. NOT a distinct list of match dates — a date dimension with gaps
-- cannot be marked as a date table and breaks time intelligence.

with match_span as (
    select
        min(match_date) as first_day,
        max(match_date) as last_day
    from {{ ref('stg_matches') }}
),

fixture_span as (
    -- Pad forward so unplayed fixtures have a date row to join to. The FPL
    -- fixture feed carries no kickoff, so run a week past the last deadline.
    select cast(max(deadline_time) as date) + interval 7 day as last_scheduled
    from {{ ref('stg_gameweeks') }}
),

bounds as (
    select
        m.first_day,
        greatest(m.last_day, coalesce(f.last_scheduled, m.last_day)) as last_day
    from match_span m
    cross join fixture_span f
),

spine as (
    select cast(unnest(
        generate_series(first_day, last_day, interval 1 day)
    ) as date) as full_date
    from bounds
)

select
    cast(strftime(full_date, '%Y%m%d') as integer)            as date_id,
    full_date,
    extract(year  from full_date)                             as year,
    extract(month from full_date)                             as month,
    strftime(full_date, '%B')                                 as month_name,
    extract(day   from full_date)                             as day_of_month,
    strftime(full_date, '%A')                                 as day_of_week,
    extract(week  from full_date)                             as iso_week,
    case when extract(dow from full_date) in (0, 6)
         then 1 else 0 end                                    as is_weekend
from spine
order by full_date