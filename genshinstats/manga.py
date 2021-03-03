"""Scraper for the genshin impact manga.

Gets the chapter names and image urls.
Inspired by: https://github.com/Meigyoku-Thmn/genshin-impact-offical-comic-downloader/
"""
import os
import re
from typing import List, Tuple

from requests import Session

MANGA_URL = "https://genshin.mihoyo.com/en/manga/detail/"
session = Session()
session.headers.update({
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
})

def get_chapter_ids() -> List[Tuple[int,str]]:
    """Gets all chapter ids and their names."""
    start_chapter = '71'
    r = session.get(MANGA_URL+start_chapter)

    ids = re.findall(r'id:(?:"(\d+)"|\w+),title:"(Chapter \d+:.*?)"',r.text)
    ids[0] = start_chapter,ids[0][1]
    return ids

def get_image_urls(chapter_id: str) -> List[str]:
    """Gets all chapter images with a chapter id."""
    r = session.get(MANGA_URL+chapter_id)
    text = r.content.decode('unicode-escape')
    urls = re.findall(r'https://uploadstatic-sea\.mihoyo\.com/contentweb/\d+/\d+\.(?:jpg|png)',text)
    return urls

def get_chapters() -> List[Tuple[str,List[str]]]:
    """Gets a list of chapters of genshin's manga, inculding the images.
    
    Returns a list of tuples of the chapter name and its urls.
    """
    return [(c,get_image_urls(i)) for i,c in get_chapter_ids()]

def download_manga(directory: str='./manga'):
    """Gets all manga and downloads it to a directory."""
    for chapter_id,chapter_name in get_chapter_ids():
        chapter_dir = os.path.join(directory,chapter_name.replace(': ',' - '))
        if not os.path.isdir(chapter_dir):
            os.makedirs(chapter_dir)
        
        for page,url in enumerate(get_image_urls(chapter_id),1):
            file = os.path.join(chapter_dir,f'{page:02}.{url.split(".")[-1]}')
            open(file,'wb').write(session.get(url).content)
            print(chapter_name,page)

if __name__ == '__main__':
    download_manga()
