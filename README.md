# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/jmjuve/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/jmjuve/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Sum up 21 November 2026's world news in one image — a make.fun bounty
entry. A pure-stdlib Python program draws a newspaper front page and
writes it to `entry.png` (1024×1024, deterministic across runs).

## The day's news (Saturday 21 November 2026)

- **Hero — QUAKE ROCKS PERU.** A magnitude 6.8 earthquake struck
  central Peru's Junín region, felt in Lima; no damage reported.
- **MISSILES OVER RIYADH.** Three Houthi ballistic missiles fired at
  Riyadh were intercepted early Saturday, the third day of alerts.
- **CLIMATE TALKS OVERRUN.** COP31 in Antalya missed its deadline;
  the draft deal drops every mention of fossil fuels.
- **NATO CHIEF TO WARSAW.** Mark Rutte is due in Poland after Russian
  missiles came down on Polish soil.

## Run it

```sh
python3 main.py            # writes out/entry.png
MAKEFUN_OUTPUT_DIR=/output python3 main.py   # writes /output/entry.png
```

No network, no dependencies beyond Python 3.13's standard library.
The image is drawn entirely in code with a hand-built 5×7 bitmap font.
