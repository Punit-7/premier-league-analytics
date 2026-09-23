{{ config(materialized='table') }}

-- Grain: one row per team per fixture.

with tf as (
    select * from {{ ref('stg_fixtures') }}
),

teams as (
    select * from {{ ref('dim_team') }}
)

select
    row_number() over (order by tf.team_name, tf.fpl_fixture_id) as team_fixture_id,
    t.team_id,
    o.team_id as opponent_team_id,
    tf.gameweek_id,
    tf.fpl_fixture_id,
    tf.is_home,
    tf.difficulty,
    tf.finished
from tf
join teams t on t.team_name = tf.team_name
left join teams o on o.team_name = tf.opponent_name
