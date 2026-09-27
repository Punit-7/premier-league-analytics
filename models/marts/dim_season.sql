{{ config(materialized='table') }}

with seasons as (
    select distinct season_code, season_label
    from {{ ref('stg_matches') }}
)

select
    row_number() over (order by season_code) as season_id,
    season_code,
    season_label,
    cast('20' || substr(season_code, 1, 2) as integer) as start_year,
    cast('20' || substr(season_code, 3, 2) as integer) as end_year,
    case season_code
        when '1920' then 'partial_behind_closed_doors'
        when '2021' then 'behind_closed_doors'
        else 'normal'
    end as crowd_status,
    case when season_code = '{{ var("current_season") }}'
         then 'in_progress' else 'completed' end as status
from seasons
