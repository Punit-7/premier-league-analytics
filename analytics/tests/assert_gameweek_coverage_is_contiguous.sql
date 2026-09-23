-- Fails if a gameweek is missing from the player fact, which means a
-- failed FPL sweep rather than a genuine gap. Returns offending rows.

with bounds as (
    select min(gameweek_id) as lo, max(gameweek_id) as hi
    from {{ ref('fact_player_fixture') }}
),

expected as (
    select lo + generate_series as gameweek_id
    from bounds, generate_series(0, (select hi - lo from bounds))
),

actual as (
    select distinct gameweek_id from {{ ref('fact_player_fixture') }}
)

select e.gameweek_id
from expected e
left join actual a on a.gameweek_id = e.gameweek_id
where a.gameweek_id is null