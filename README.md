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

### Opening the Power BI report

The report reads the CSV export in `analytics/data/powerbi/`. Because that is an absolute path on my machine, you need to point it at yours:

1. Open `analytics/powerbi/pl-analytics.pbix` in Power BI Desktop.
2. Home → Transform data → Manage Parameters.
3. Set `DataPath` to your clone's `analytics/data/powerbi` folder.
4. Close & Apply.

The CSVs are committed, so there is nothing to rebuild first.