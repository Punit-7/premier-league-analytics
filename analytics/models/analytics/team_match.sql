{{ config(materialized='table') }}

-- One row per team per match. Team-level analysis builds on this.

with home as (
    select
        match_id, season_id, date_id,
        home_team_id as team_id, away_team_id as opponent_id, 'H' as venue,
        ft_home_goals as goals_for, ft_away_goals as goals_against,
        home_points as points, home_shots as shots,
        home_shots_on_target as shots_on_target,
        home_yellows as yellows, home_reds as reds
    from {{ ref('fact_match') }}
),

away as (
    select
        match_id, season_id, date_id,
        away_team_id, home_team_id, 'A',
        ft_away_goals, ft_home_goals, away_points,
        away_shots, away_shots_on_target, away_yellows, away_reds
    from {{ ref('fact_match') }}
)

select * from home
union all
select * from away
