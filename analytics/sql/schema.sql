CREATE TABLE IF NOT EXISTS pipeline_run (
    run_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ok','failed')),
    finished_at TEXT NOT NULL,
    duration_s REAL NOT NULL,
    rows INTEGER,
    message TEXT,
    PRIMARY KEY (run_id, stage)
);