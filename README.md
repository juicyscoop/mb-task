# CSFD Top movies search deom

Django app browses top 300 movies and their actors from csfd.cz, using a local sqlite3 database for storage.

## Install dependencies
- `pip install Django`

## Simplest setup
- Use already present db.sqlite3
- Run the app `python manage.py runserver`
- Go to `/search/`

## Setup with scraping
- Init DB: `python manage.py makeigrations && python manage.py migrate`
- Scrape: `python manage.py scrape_csfd` - see logs
- Run: `python manage.py runserver`
- Go to `/search/`

Supports autocomplete and accent-insensitive search.
