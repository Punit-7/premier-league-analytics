-- Thin layer: rename, cast, and nothing else. No business logic here.
with source as (
    select * from {{ source('raw', 'raw_matches') }}
),

renamed as (
    select
        match_id,
        season_code,
        season_label,
        cast(match_date as date)              as match_date,
        home_team,
        away_team,
        referee,
        kickoff_time,
        cast(ft_home_goals as integer)        as ft_home_goals,
        cast(ft_away_goals as integer)        as ft_away_goals,
        ft_result,
        cast(ht_home_goals as integer)        as ht_home_goals,
        cast(ht_away_goals as integer)        as ht_away_goals,
        ht_result,
        cast(home_shots as integer)           as home_shots,
        cast(away_shots as integer)           as away_shots,
        cast(home_shots_on_target as integer) as home_shots_on_target,
        cast(away_shots_on_target as integer) as away_shots_on_target,
        cast(home_fouls as integer)           as home_fouls,
        cast(away_fouls as integer)           as away_fouls,
        cast(home_corners as integer)         as home_corners,
        cast(away_corners as integer)         as away_corners,
        cast(home_yellows as integer)         as home_yellows,
        cast(away_yellows as integer)         as away_yellows,
        cast(home_reds as integer)            as home_reds,
        cast(away_reds as integer)            as away_reds,
        cast(home_points as integer)          as home_points,
        cast(away_points as integer)          as away_points,
        cast(total_goals as integer)          as total_goals,
        cast(goal_difference as integer)      as goal_difference
    from source
)

select * from renamed
