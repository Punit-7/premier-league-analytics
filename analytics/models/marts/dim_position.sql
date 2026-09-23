{{ config(materialized='table') }}

-- FPL's element_types are already a clean dimension; nothing to reshape.
select * from {{ ref('stg_positions') }}
