{{ config(materialized='table') }}

-- Grain: one row per completed fixture.

with matches as (
    select * from {{ ref('stg_matches') }}
),

home_teams as (select team_id, team_name from {{ ref('dim_team') }}),
away_teams as (select team_id, team_name from {{ ref('dim_team') }})

select
    m.match_id,
    s.season_id,
    d.date_id,
    h.team_id as home_team_id,
    a.team_id as away_team_id,
    coalesce(r.referee_id, 0) as referee_id,
    m.kickoff_time,
    m.ft_home_goals,
    m.ft_away_goals,
    m.ft_result,
    m.ht_home_goals,
    m.ht_away_goals,
    m.ht_result,
    m.home_shots,
    m.away_shots,
    m.home_shots_on_target,
    m.away_shots_on_target,
    m.home_fouls,
    m.away_fouls,
    m.home_corners,
    m.away_corners,
    m.home_yellows,
    m.away_yellows,
    m.home_reds,
    m.away_reds,
    m.home_points,
    m.away_points,
    m.total_goals,
    m.goal_difference
from matches m
join {{ ref('dim_season') }} s on s.season_code = m.season_code
join {{ ref('dim_date') }}   d on d.full_date   = m.match_date
join home_teams h on h.team_name = m.home_team
join away_teams a on a.team_name = m.away_team
left join {{ ref('dim_referee') }} r on r.referee_name = m.referee
