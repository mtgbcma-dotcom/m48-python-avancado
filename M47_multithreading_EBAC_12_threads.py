"""
M47 - EBAC - Backend Python - Módulo 4
Web Scraping com Multithreading

Baseado no repositório oficial fornecido no exercício:
https://github.com/havokkmorands/multithreading

Alteração solicitada:
MAX_THREADS = 12
"""

import csv
import random
import time
import concurrent.futures
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

MAX_THREADS = 12

BASE_URL = "https://havokkmorands.github.io/movie-catalog/"


def extract_movie_details(movie_link):
    """Extrai os dados de uma página individual de filme."""

    time.sleep(random.uniform(0, 0.2))

    try:
        response = requests.get(
            movie_link,
            headers=HEADERS,
            timeout=20
        )
        response.raise_for_status()

        movie_soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        detail_container = movie_soup.find(
            "section",
            attrs={"data-testid": "movie-detail"}
        )

        if detail_container is None:
            print(
                f"Detalhe do filme não encontrado: "
                f"{movie_link}"
            )
            return None

        title_tag = detail_container.find(
            attrs={"data-testid": "movie-title"}
        )

        release_tag = detail_container.find(
            attrs={"data-testid": "movie-release"}
        )

        rating_tag = detail_container.find(
            attrs={"data-testid": "movie-rating"}
        )

        synopsis_tag = detail_container.find(
            attrs={"data-testid": "movie-synopsis"}
        )

        title = (
            title_tag.get_text(strip=True)
            if title_tag
            else None
        )

        release_date = (
            release_tag.get_text(strip=True)
            .replace("Lançamento:", "")
            .strip()
            if release_tag
            else None
        )

        rating = (
            rating_tag.get_text(strip=True)
            .replace("Nota:", "")
            .strip()
            if rating_tag
            else None
        )

        synopsis = (
            synopsis_tag.get_text(strip=True)
            .replace("Sinopse:", "")
            .strip()
            if synopsis_tag
            else None
        )

        if all([title, release_date, rating, synopsis]):
            print(
                title,
                release_date,
                rating,
                synopsis
            )

            return [
                title,
                release_date,
                rating,
                synopsis
            ]

        print(
            f"Dados incompletos no filme: "
            f"{movie_link}"
        )
        return None

    except requests.RequestException as error:
        print(
            f"Erro ao acessar {movie_link}: "
            f"{error}"
        )
        return None


def extract_movies(soup):
    """Localiza os filmes e executa as páginas em paralelo."""

    container = soup.find(
        "section",
        attrs={"data-testid": "movies-list"}
    )

    if container is None:
        print("Container principal não encontrado.")
        return []

    movies_table = container.find_all(
        "article",
        attrs={"data-testid": "movie-item"}
    )

    if not movies_table:
        print("Lista de filmes não encontrada.")
        return []

    movie_links = []

    for movie in movies_table:
        a_tag = movie.find(
            "a",
            attrs={"data-testid": "movie-link"},
            href=True
        )

        if a_tag:
            movie_links.append(
                urljoin(BASE_URL, a_tag["href"])
            )

    if not movie_links:
        print("Nenhum link de filme foi encontrado.")
        return []

    threads = min(
        MAX_THREADS,
        len(movie_links)
    )

    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=threads
    ) as executor:

        futures = [
            executor.submit(
                extract_movie_details,
                movie_link
            )
            for movie_link in movie_links
        ]

        for future in concurrent.futures.as_completed(
            futures
        ):
            result = future.result()

            if result:
                results.append(result)

    return results


def save_movies(movies):
    """Salva o resultado da raspagem em movies.csv."""

    with open(
        "movies.csv",
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "title",
            "release_date",
            "rating",
            "synopsis"
        ])

        writer.writerows(movies)


def main():
    start_time = time.time()

    try:
        response = requests.get(
            BASE_URL,
            headers=HEADERS,
            timeout=20
        )
        response.raise_for_status()

        print("Status:", response.status_code)
        print("URL final:", response.url)
        print("Máximo de threads:", MAX_THREADS)

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        movies = extract_movies(soup)

        save_movies(movies)

        end_time = time.time()

        print(
            "Filmes coletados:",
            len(movies)
        )

        print(
            "Total time taken:",
            end_time - start_time
        )

        print(
            "Arquivo gerado: movies.csv"
        )

    except requests.RequestException as error:
        print(
            "Erro ao acessar o catálogo:",
            error
        )


if __name__ == "__main__":
    main()
