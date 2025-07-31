from django.core.management.base import BaseCommand, CommandError
from csfd.management.commands.scrape_manager import ScrapeManager


class Command(BaseCommand):
    help = 'Synchronously scrapes CSFD Top 300 list for movie titles and actors.'
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting CSFD Top 300 scraper...'))

        try:
            self.stdout.write("Scraping movie data into local SQLite database")
            manager = ScrapeManager(self.stdout)
            manager.run_async()
            self.stdout.write(self.style.SUCCESS("Data scraped and saved to local SQLite database"))

        except Exception as e:
            raise CommandError(f'An error occurred: {e}')
