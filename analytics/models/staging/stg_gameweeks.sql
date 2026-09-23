-- Thin layer: rename, cast, and nothing else. No business logic here.
with source as (
    select * from {{ source('raw', 'raw_gameweeks') }}
),

renamed as (
    select
        cast(gameweek_id as integer)   as gameweek_id,
        gameweek_name,
        deadline_time,
        cast(finished as boolean)      as finished,
        cast(is_current as boolean)    as is_current,
        cast(is_next as boolean)       as is_next,
        cast(average_score as integer) as average_score,
        cast(highest_score as integer) as highest_score
    from source
)

select * from renamed
