{{ config(materialized='table') }}

-- One row per player: season totals with their current price attached.

with facts as (
    select * from {{ ref('fact_player_fixture') }}
),

players as (
    select * from {{ ref('dim_player') }}
),

teams as (
    select * from {{ ref('dim_team') }}
),

positions as (
    select * from {{ ref('dim_position') }}
)

select
    p.player_id, p.web_name, p.full_name, p.price_m,
    p.selected_by_percent, p.status,
    t.team_name, pos.position_short, pos.position_name,
    count(f.player_fixture_id)                         as fixtures,
    sum(case when f.minutes > 0 then 1 else 0 end)     as appearances,
    sum(f.minutes)                                     as minutes,
    sum(f.total_points)                                as points,
    sum(f.goals_scored)                                as goals,
    sum(f.assists)                                     as assists,
    sum(f.clean_sheets)                                as clean_sheets,
    sum(f.bonus)                                       as bonus,
    round(sum(f.total_points) / nullif(p.price_m, 0), 2) as points_per_million
from players p
join teams t       on t.team_id       = p.team_id
join positions pos on pos.position_id = p.position_id
left join facts f  on f.player_id     = p.player_id
group by p.player_id, p.web_name, p.full_name, p.price_m,
         p.selected_by_percent, p.status, t.team_name,
         pos.position_short, pos.position_name
