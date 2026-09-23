{{ config(materialized='table') }}

-- Grain: one row per player. The mart the Power BI report and the app both read.

with facts as (
    select * from {{ ref('fact_player_fixture') }}
),

aggregated as (
    select
        player_id,
        count(*)                                       as squad_games,
        sum(case when minutes >= 60 then 1 else 0 end) as full_games,
        sum(case when minutes = 0 then 1 else 0 end)   as unused,
        sum(minutes)                                   as minutes,
        sum(total_points)                              as total_points,
        max(price_m)                                   as latest_price_m,
        max(selected)                                  as owners
    from facts
    group by player_id
)

select
    p.player_id,
    p.web_name,
    pos.position_short as position,
    t.team_name,
    a.squad_games,
    a.full_games,
    a.unused,
    a.minutes,
    a.total_points,
    a.latest_price_m,
    a.owners,
    round(a.total_points / nullif(a.latest_price_m, 0), 2)    as points_per_million,
    round(100.0 * a.full_games / nullif(a.squad_games, 0), 0) as start_rate_pct
from aggregated a
join {{ ref('dim_player') }} p     on p.player_id     = a.player_id
left join {{ ref('dim_team') }} t     on t.team_id     = p.team_id
left join {{ ref('dim_position') }} pos on pos.position_id = p.position_id
