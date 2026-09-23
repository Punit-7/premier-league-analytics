-- Thin layer: rename, cast, and nothing else. No business logic here.
with source as (
    select * from {{ source('raw', 'raw_positions') }}
),

renamed as (
    select
        cast(position_id as integer)    as position_id,
        position_name,
        position_short,
        cast(squad_select as integer)   as squad_select,
        cast(squad_min_play as integer) as squad_min_play,
        cast(squad_max_play as integer) as squad_max_play
    from source
)

select * from renamed
