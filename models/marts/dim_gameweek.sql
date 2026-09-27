{{ config(materialized='table') }}

-- The FPL gameweek calendar is already a clean dimension; nothing to reshape.
select * from {{ ref('stg_gameweeks') }}
