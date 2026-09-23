-- Thin layer: rename, cast, and nothing else. No business logic here.
-- Grain: one row per team per fixture (the FPL difficulty feed).
with source as (
    select * from {{ source('raw', 'raw_fixtures') }}
),

renamed as (
    select
        team_name,
        opponent_name,
        cast(gameweek_id as integer)    as gameweek_id,
        cast(fpl_fixture_id as integer) as fpl_fixture_id,
        cast(is_home as boolean)        as is_home,
        cast(difficulty as integer)     as difficulty,
        cast(finished as boolean)       as finished
    from source
)

select * from renamed
