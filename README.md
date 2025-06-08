# Bot_Menorca_EESS

A Telegram bot that tells you the ever-fluctuating, soul-crushing prices of petrol in Menorca. Miraculously, it's still running.

## What it does (or tries to do)
- Fetches prices from some government API that probably hasn't been updated since the last ice age.
- Lets you set price alerts, so you can be instantly notified when prices drop by a fraction of a cent. Don't spend it all in one place.
- Shows you historical price charts, because who doesn't love to reminisce about when fuel was *slightly* less unaffordable?
- Finds gas stations near you, assuming your phone's GPS and our code decide to cooperate.

## Technology Stack
- **Python**: Because we had to choose something.
- **MySQL**: To store all this data that is probably wrong anyway.
- **A tangled mess of scripts**: Held together by hope and `cron` jobs.

## Recent "Improvements" (June 2025)

We've been hard at work plugging the seemingly endless holes in this sinking ship. Here's what we begrudgingly fixed:

- **The "Last Updated" Lie**: The bot used to claim it updated prices every time it was restarted. We've now forced it to tell the truth (mostly) by showing the actual API fetch time. Progress, I guess.
- **The Placebo "Remove Alert" Button**: We discovered the button to remove price alerts was just for show. It has now been wired up to an actual function. You're welcome.
- **The Ghost Table**: Our historical price charts were powered by an empty database table. Turns out, using placeholder credentials like `'USER'` and `'PASSWORD'` isn't just bad practice, it's non-functional. Who knew?
- **The Great Comma vs. Dot Debate**: Our database threw a fit because the API provides numbers like `'39,908333'` and not `'39.908333'`. We've added code to painstakingly translate these, because standards are apparently just a suggestion.

Test it [here](https://t.me/preus_combustible_bot), if you dare.

---
Credit to @Zolekode for the [JSON-to-tables package](https://github.com/zolekode/json-to-tables), one of the few things here that actually works as advertised.
