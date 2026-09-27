{{ config(materialized='table') }}

-- Grain: one row per player per fixture.
-- A double gameweek gives a player two rows in one round, correctly.

with pf as (
    select * from {{ ref('stg_player_fixture') }}
),

players as (
    select * from {{ ref('dim_player') }}
),

teams as (
    select * from {{ ref('dim_team') }}
),

dates as (
    select * from {{ ref('dim_date') }}
)

select
    pf.player_fixture_id,
    p.player_id,
    pf.gameweek_id,
    d.date_id,
    o.team_id as opponent_team_id,
    pf.fpl_fixture_id,
    pf.was_home,
    pf.minutes,
    pf.total_points,
    pf.goals_scored,
    pf.assists,
    pf.clean_sheets,
    pf.goals_conceded,
    pf.yellow_cards,
    pf.red_cards,
    pf.saves,
    pf.bonus,
    pf.bps,
    pf.influence,
    pf.creativity,
    pf.threat,
    pf.ict_index,
    pf.price_m,
    pf.selected,
    pf.transfers_in,
    pf.transfers_out
from pf
join players p on p.fpl_element_id = pf.fpl_element_id
left join teams o on o.team_name = pf.opponent_name
left join dates d on d.full_date = pf.match_date
