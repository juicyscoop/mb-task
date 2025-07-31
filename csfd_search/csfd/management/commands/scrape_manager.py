

import requests
from bs4 import BeautifulSoup
from csfd.models import Movie, Actor
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://www.csfd.cz"

URLS_TO_SCRAPE = [
    "https://www.csfd.cz/zebricky/filmy/nejlepsi/?showMore=1",
    "https://www.csfd.cz/zebricky/filmy/nejlepsi/?from=100",
    "https://www.csfd.cz/zebricky/filmy/nejlepsi/?from=200",
    "https://www.csfd.cz/zebricky/filmy/nejlepsi/?from=300",
]

class ScrapeManager:
    def __init__(self, stdout_writer):
        self.session = requests.Session()
        # We want to look like a browser
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/115.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://example.com/"
        })

        self.writer = stdout_writer

    def get_soup(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def find_actor_links(self, soup):
        for h4 in soup.find_all("h4"):
            if "Hrají:" in h4.text.strip() :
                parent_div = h4.find_parent("div")
                if parent_div:
                    return parent_div.find_all("a")
        return []
    
    def run_async(self):
        self.writer.write("Scraping movie data ASYNC mode into local SQLite database")
        all_movie_links = []

        for ind, url_to_scrape in enumerate(URLS_TO_SCRAPE):
            self.writer.write(f"Visiting page to scrape: {url_to_scrape}")
            main_soup = self.get_soup(url_to_scrape)
            links = main_soup.find_all("a", class_="film-title-name")
            self.writer.write(f"Found {len(links)} links on {url_to_scrape}")
            
            if ind == (len(URLS_TO_SCRAPE) - 1):
                links = links[:1]
            
            all_movie_links.extend(links)

        self.writer.write(f"Scraping {len(all_movie_links)} total movie pages with threads...")

        def process_movie(link):
            href = link.get("href")
            if not href:
                return

            movie_url = href if href.startswith("http") else BASE_URL + href
            movie_title = link.get("title", "Unknown Title").strip()
            movie, created = Movie.objects.get_or_create(url=movie_url, defaults={"title": movie_title})

            if not created and movie.title != movie_title:
                movie.title = movie_title
                movie.save()

            try:
                page_soup = self.get_soup(movie_url)
                actor_links = self.find_actor_links(page_soup)

                for actor_link in actor_links:
                    actor_name = actor_link.get_text(strip=True)
                    actor_href = actor_link.get("href")
                    actor_full_url = actor_href if actor_href and actor_href.startswith("http") else BASE_URL + actor_href
                    actor, _ = Actor.objects.get_or_create(name=actor_name, url=actor_full_url)
                    movie.actors.add(actor)

                return f"✅ {movie_title}"

            except requests.RequestException as e:
                return f"❌ Error fetching {movie_url}: {e}"

        # Thread pool
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_movie, link) for link in all_movie_links]
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                self.writer.write(result)
                if i % 10 == 0:
                    self.writer.write(f"Scraped {i} movies.")


    def run_sync(self):
        self.writer.write("Scraping movie data SYNC mode into local SQLite database")

        movies_scraped = 0

        for url_to_scrape in URLS_TO_SCRAPE:

            self.writer.write(f"Visiting page to scrape: {url_to_scrape}")

            main_soup = self.get_soup(url_to_scrape)

            initial_links = main_soup.find_all("a", class_="film-title-name")
            
            self.writer.write(f"Scraping {len(initial_links)} movie links.")
            for link in initial_links:

                href = link.get("href")
                if not href:
                    continue

                movie_url = href if href.startswith("http") else BASE_URL + href
                movie_title = link.get("title", "Unknown Title").strip()
                movie, created = Movie.objects.get_or_create(url=movie_url, defaults={"title": movie_title})
                
                if not created and movie.title != movie_title:
                    movie.title = movie_title
                    movie.save()

                try:
                    self.writer.write(f"Visiting movie link: {movie_url}")
                    page_soup = self.get_soup(movie_url)

                    actor_links = self.find_actor_links(page_soup)

                    for actor_link in actor_links:
                        actor_name = actor_link.get_text(strip=True)
                        actor_href = actor_link.get("href")
                        
                        actor_full_url = actor_href if actor_href and actor_href.startswith("http") else BASE_URL + actor_href
                        
                        actor, _ = Actor.objects.get_or_create(name=actor_name, url=actor_full_url)
                        movie.actors.add(actor)
                    
                    movies_scraped += 1

                    if movies_scraped % 10 == 0:
                        self.writer.write(f"Scraped {movies_scraped} movies.")
                    
                    if movies_scraped == 300:
                        break

                except requests.RequestException as e:
                    self.writer.write(f"Error fetching {movie_url}: {e}")