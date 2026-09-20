# Premier League Analytics

A Premier League analytics platform. One ingest pipeline and one data contract,
feeding four independent surfaces.

| Surface | What it is | Live |
|---|---|---|
| [analytics/](analytics)  | Star-schema warehouse, SQL, Power BI, live dashboard | TODO |
| [modelling/](modelling)  | FPL points model and squad optimiser                 | TODO |
| [serving/](serving)      | The model as a tested, monitored API                 | TODO |
| [assistant/](assistant)  | Retrieval-augmented assistant over the season corpus | TODO |

Scaffolded with `python scripts/bootstrap.py`.
