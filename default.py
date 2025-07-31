import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup
import xbmcplugin
import xbmcgui

addon_handle = int(sys.argv[1])
base_url = 'https://fmovies5.com'
xbmcplugin.setContent(addon_handle, 'movies')

def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    return requests.get(url, headers=headers).text

def main_menu():
    add_dir('Search 🔍', 'search', '')
    add_dir('Genres 🎭', 'genres', '')
    list_movies(base_url)

def add_dir(name, mode, url):
    u = f'{sys.argv[0]}?mode={mode}&url={urllib.parse.quote(url)}'
    li = xbmcgui.ListItem(name)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=li, isFolder=True)

def list_movies(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    movies = soup.select('div.flw-item')

    for movie in movies:
        a_tag = movie.find('a', href=True)
        title = a_tag.get('title', 'Unknown Title')
        link = urllib.parse.urljoin(base_url, a_tag['href'])
        image = movie.img['data-src'] if movie.img else ''

        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt({'thumb': image})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=f'{sys.argv[0]}?mode=play&url={urllib.parse.quote(link)}', listitem=list_item, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

def play_movie(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    iframe = soup.find('iframe')
    if iframe:
        stream_url = iframe['src']
        play_item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    else:
        xbmcgui.Dialog().notification("FMovies", "Stream not found", xbmcgui.NOTIFICATION_ERROR)

def search():
    keyboard = xbmcgui.Dialog().input('Search FMovies5')
    if keyboard:
        search_url = f"{base_url}/search/{urllib.parse.quote(keyboard)}"
        list_movies(search_url)

def list_genres():
    html = get_html(base_url)
    soup = BeautifulSoup(html, 'html.parser')
    genre_links = soup.select('ul.menu-sub li a[href*="/genre/"]')

    for link in genre_links:
        name = link.text.strip()
        url = urllib.parse.urljoin(base_url, link['href'])
        add_dir(name, 'genre', url)

    xbmcplugin.endOfDirectory(addon_handle)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    mode = params.get('mode')
    url = urllib.parse.unquote(params.get('url', ''))

    if mode == 'play':
        play_movie(url)
    elif mode == 'search':
        search()
    elif mode == 'genres':
        list_genres()
    elif mode == 'genre':
        list_movies(url)
    else:
        main_menu()

router(sys.argv[2][1:])
