{{ config(materialized='table') }}

with players as (
    select * from {{ ref('stg_players') }}
),

teams as (
    select * from {{ ref('dim_team') }}
)

select
    row_number() over (order by p.fpl_element_id) as player_id,
    p.fpl_element_id,
    p.fpl_player_code,
    p.web_name,
    p.first_name || ' ' || p.second_name as full_name,
    t.team_id,
    p.position_id,
    p.price_m,
    p.selected_by_percent,
    p.status,
    p.total_points,
    p.minutes,
    p.form,
    p.points_per_game
from players p
left join teams t on t.team_name = p.team_name
