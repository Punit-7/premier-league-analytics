# Known data issues

## 1. Two sources name clubs differently
football-data says "Man United" / "Tottenham"; FPL says "Man Utd" / "Spurs".
Two alias maps resolve both into canonical dimension. Unmapped names raises.

## 2. Two clubs have no Premier League history
Coventry City and Hull City were promoted for 2026/27. Any prior-season feature is undefined for them and for their players. A genuine problem for P2,
recorded here so it is not mistaken for a data error.

## 3. FPL prices are in the tenths of a million
'now_cost: 55' means GBP 5.5m. Converted during cleaning.

## 4. Player 'id' is not stable across seasons; 'code' is
Both are stored.'code' is the join key for past season archives.

## 5. Double gameweeks break the obvious grain
A player can appear twice inside one gameweek. The player fact table is at
player-per-fixture grain, with gameweek as an attribute. A per-gameweek grain
would silently lose a fixture.

## 6. 'value' in a player's history is the price at that gameweek
Not the current price. Both are needed and they mean different things.

## 7. The live file is incomplete by definition
Completed-season rules cannot apply to 2026/27. Two quality suites.

## 8. Fixtures are not evenly distributed
Weekend rounds spread across Friday to Monday, midweek rounds exist, and
matches get postponed. Some teams are always ahead of others. Tolerated up to a configured spread rather than assumed away.

## 9. Two seasons were played without crowds
2019/20 was suspended and resumed behind closed doors; 2020/21 was played
almost entirely without crowds. Flagged on the season dimension — a confound,
not an error.

## 10. FPL data is current-season only
The API exposes no historical seasons. Past-season player data comes from the
community-maintained vaastav/Fantasy-Premier-League archive, which is NOT
official. P2 uses it for training; the provenance is labelled there.

## 11. Bookmaker odds columns excluded by design
Unstable across seasons, and not match facts. P2 uses them as a benchmark.