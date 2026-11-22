# THE WORLD IN ONE DAY — Sunday 22 November 2026

A one-image summary of the world's news of Sunday 22 November 2026,
drawn as a newspaper front page.

Lead story: the COP31 climate summit in Antalya enters a second day of
overtime as nations deadlock over fossil fuels. Around it, eight more
stories from the day: Iran strikes a Bahrain industrial site and tankers
are attacked in the Strait of Hormuz; a Russian drone levels a
five-storey block near Kyiv; a Russian cargo ship burns in the Gulf of
Finland after a drone strike; the FBI's national crime database is
hacked; a sweets-factory fire in Cikande, Indonesia, leaves three dead
and 36 missing; an aid van is struck in Gaza as storms flood shelters;
UN talks on autonomous weapons collapse in Geneva; and the EU signs a
trade deal with Indonesia after ten years of talks.

## How it works

`render.py` (pure Python 3.13 standard library) draws the poster with a
hand-built 5x7 bitmap font and a hand-rolled PNG encoder, and saves it
as `poster.png`. `main.py` copies `poster.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).

## Run

```
python3 render.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The output is a deterministic 1024x1024 PNG under 1 MiB.
