-- Thin layer: rename, cast, and nothing else. No business logic here.
with source as (
    select * from {{ source('raw', 'raw_player_fixture') }}
),

renamed as (
    select
        cast(player_fixture_id as integer) as player_fixture_id,
        fpl_element_id,
        opponent_name,
        cast(match_date as date)           as match_date,
        cast(gameweek_id as integer)       as gameweek_id,
        cast(fpl_fixture_id as integer)    as fpl_fixture_id,
        cast(was_home as boolean)          as was_home,
        cast(minutes as integer)           as minutes,
        cast(total_points as integer)      as total_points,
        cast(goals_scored as integer)      as goals_scored,
        cast(assists as integer)           as assists,
        cast(clean_sheets as integer)      as clean_sheets,
        cast(goals_conceded as integer)    as goals_conceded,
        cast(yellow_cards as integer)      as yellow_cards,
        cast(red_cards as integer)         as red_cards,
        cast(saves as integer)             as saves,
        cast(bonus as integer)             as bonus,
        cast(bps as integer)               as bps,
        cast(influence as double)          as influence,
        cast(creativity as double)         as creativity,
        cast(threat as double)             as threat,
        cast(ict_index as double)          as ict_index,
        cast(price_m as double)            as price_m,
        cast(selected as integer)          as selected,
        cast(transfers_in as integer)      as transfers_in,
        cast(transfers_out as integer)     as transfers_out
    from source
)

select * from renamed
