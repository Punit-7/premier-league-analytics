{{ config(materialized='table') }}

-- Grain: one row per club. Names arrive already canonicalised by
-- src/team_names.py before they reach raw_*, so no reconciliation happens here.

with names as (
    select home_team as team_name from {{ ref('stg_matches') }}
    union
    select away_team from {{ ref('stg_matches') }}
    union
    select team_name from {{ ref('stg_players') }}
    union
    select team_name from {{ ref('stg_fixtures') }}
    union
    select opponent_name from {{ ref('stg_fixtures') }}
),

distinct_names as (
    select distinct team_name from names where team_name is not null
)

select
    row_number() over (order by team_name) as team_id,
    team_name
from distinct_names
