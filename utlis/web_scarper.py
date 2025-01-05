from typing import List, Optional

import aiohttp
from attr import dataclass
from bs4 import BeautifulSoup
from pydantic import BaseModel

engine_url = 'http://asilmedia.org'


@dataclass
class MovieVideo:
    quality: str
    url: str


class Movie:
    title: str
    page_url: str
    picture: str
    info: str
    description: Optional[str]
    videos: List[MovieVideo]

    def __init__(self, title: str, page_url: str, picture: str, info: str, description: Optional[str] = None,
                 videos: Optional[List[MovieVideo]] = None):
        self.title = title
        self.page_url = page_url
        self.picture = picture
        self.info = info
        self.description = description
        self.videos = videos

    def dump_json(self) -> dict:
        return {'title': self.title, 'page_url': self.page_url, 'picture': self.picture, 'info': self.info}

    @staticmethod
    async def search(prompt: str, page: int = 1) -> List['Movie']:
        form_data = {
            "do": "search",
            "subaction": "search",
            "search_start": page,
            "story": prompt
        }
        search_url = engine_url + '/index.php?do=search'
        async with aiohttp.ClientSession() as session:
            async with session.post(search_url, data=form_data) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                articles = soup.find_all('article')
                movies = []
                for article in articles:
                    title = article.find('h2', class_='title is-6 txt-ellipsis mb-2').get_text()
                    page_url = article.find('a').get('href')
                    picture = engine_url + article.find('img').get('data-src')
                    description = article.find('div', class_='subtitle txt-ellipsis flx txt-small').get_text().replace(
                        '\n',
                        ' ').strip()
                    movies.append(Movie(title=title, page_url=page_url, info=description, picture=picture))
                return movies

    async def approve_videos(self):
        async with (aiohttp.ClientSession() as session):
            async with session.get(self.page_url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                try:
                    self.description = soup.find('div',
                                             class_='fullcol-right flx-fx order-last').get_text(
                    ).lstrip().strip().replace('\n\n', '')
                    player_div = soup.find('div', id='player-moonwalk')
                    iframe = soup.find('iframe')
                    iframe_src = iframe['src'].split('file=')[1]
                    options = player_div.find_all('option')
                    movie_videos = []
                    for option in options:
                        video_url = option['value'].split('file=')[1]
                        name = option.get_text()
                        if video_url == '[xfvalue_kino_url]':
                            video_url = iframe_src
                        movie_videos.append(MovieVideo(quality=name, url=video_url))
                    self.videos = movie_videos
                except AttributeError:
                    self.videos = []
