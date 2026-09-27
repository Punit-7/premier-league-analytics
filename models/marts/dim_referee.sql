{{ config(materialized='table') }}

-- referee_id 0 is a deliberate "Unknown" row: some early seasons have no
-- referee recorded, and fact_match.referee_id is not-null.

with names as (
    select distinct referee
    from {{ ref('stg_matches') }}
    where referee is not null and trim(referee) != ''
)

select 0 as referee_id, 'Unknown' as referee_name
union all
select
    row_number() over (order by referee) as referee_id,
    referee as referee_name
from names
