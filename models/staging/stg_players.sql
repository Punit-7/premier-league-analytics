-- Thin layer: rename, cast, and nothing else. No business logic here.
with source as (
    select * from {{ source('raw', 'raw_players') }}
),

renamed as (
    select
        fpl_element_id,
        fpl_player_code,
        web_name,
        first_name,
        second_name,
        team_name,
        cast(position_id as integer)        as position_id,
        cast(price_m as double)             as price_m,
        cast(selected_by_percent as double) as selected_by_percent,
        status,
        cast(total_points as integer)       as total_points,
        cast(minutes as integer)            as minutes,
        cast(form as double)                as form,
        cast(points_per_game as double)     as points_per_game
    from source
)

select * from renamed
