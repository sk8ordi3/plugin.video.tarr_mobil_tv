# -*- coding: utf-8 -*-

'''
    TarrMobiltv Addon
    Copyright (C) 2024 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
import html
import json
import time

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')
base_log_info = f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]}'

xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://www.tarrmobiltv.hu'

addon = xbmcaddon.Addon('plugin.video.tarr_mobil_tv')

tarr_user = addon.getSetting('username')
tarr_pass = addon.getSetting('password')

if not tarr_user or not tarr_pass:
    xbmc.log("Username or password not set, opening settings", level=xbmc.LOGINFO)
    addon.openSettings()
    exit()

def fetch_and_set_session_cookie(tarr_device_WI):
    sessioncookie = addon.getSetting("sessioncookie")
    sessioncookie_timestamp = addon.getSetting("sessioncookie_timestamp")

    if not (sessioncookie and sessioncookie_timestamp) or (int(time.time()) - int(sessioncookie_timestamp) > 60 * 10):
        headers_x = {
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0'
        }

        if (sessioncookie and sessioncookie_timestamp):
            xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | checking session cookie validity', xbmc.LOGINFO)
            cookies_x = {
                'TarrMobiltv[player]': 'html5',
                'TarrMobiltv[remember]': '1',
                'TarrMobiltv[user]': quote(tarr_user),
                'TarrMobiltv[pass]': quote(tarr_pass),
                'TarrMobiltv[device]': tarr_device_WI,
                sessioncookie.split("=")[0]: sessioncookie.split("=")[1]
            }
            response = requests.post(f'{base_url}/ajax/broadcast/sessionurl/', cookies=cookies_x, headers=headers_x).json()
            if response["status"]["code"] == 200:
                xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | session cookie is valid', xbmc.LOGINFO)
                xbmcaddon.Addon().setSetting('sessioncookie_timestamp', f'{int(time.time())}')
                return sessioncookie
        xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | no session cookie or session cookie is not valid, requesting new one', xbmc.LOGINFO)
        sessioncookie = None
        cookies_x = {
            'TarrMobiltv[player]': 'html5',
            'TarrMobiltv[remember]': '1',
            'TarrMobiltv[user]': quote(tarr_user),
            'TarrMobiltv[pass]': quote(tarr_pass),
            'TarrMobiltv[device]': tarr_device_WI
        }
        response = requests.post(f'{base_url}/ajax/user/login/', cookies=cookies_x, headers = headers_x, data={"user": tarr_user, "pass": tarr_pass, "remember": "1"})
        for cookie in response.cookies:
            if cookie.discard:
                sessioncookie = f'{cookie.name}={cookie.value}'
                xbmcaddon.Addon().setSetting("sessioncookie", sessioncookie)
                xbmcaddon.Addon().setSetting('sessioncookie_timestamp', f'{int(time.time())}')
                break
        if not sessioncookie:
            xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | session cookie not found in answer', xbmc.LOGERROR)
    else:
        xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | session cookie check less than 10 minutes ago. No need to check it.', xbmc.LOGINFO)
    return sessioncookie


def fetch_and_set_token():

    tarr_device_WI = addon.getSetting("tarr_device_WI")
    device_WI_timestamp_str = addon.getSetting('device_WI_timestamp')

    if not (tarr_device_WI and device_WI_timestamp_str) or (int(time.time()) - int(device_WI_timestamp_str) > 365 * 24 * 60 * 60):
        xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | Requesting new device ID', xbmc.LOGINFO)
        randomHash = os.urandom(16).hex()
        gen_WI_hash = f'WI_{randomHash}'

        cookies_x = {
            'TarrMobiltv[player]': 'html5',
            'TarrMobiltv[remember]': '1',
            'TarrMobiltv[user]': quote(tarr_user),
            'TarrMobiltv[pass]': quote(tarr_pass),
        }

        headers_x = {
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0'
        }

        response_1 = requests.get(f'{base_url}/ajax/fp/main/device/{gen_WI_hash}', cookies=cookies_x, headers=headers_x, allow_redirects=False)

        tarr_device_WI = response_1.cookies.get_dict()["TarrMobiltv[device]"]

        xbmcaddon.Addon().setSetting('tarr_device_WI', f'{tarr_device_WI}')

        addon.setSetting('device_WI_timestamp', f'{int(time.time())}')
        addon.setSetting("sessioncookie", "")
    return tarr_device_WI

tarr_device_WI = None
sessioncookie = None
tarr_device_WI = fetch_and_set_token()
sessioncookie = fetch_and_set_session_cookie(tarr_device_WI)

cookies = {
    'TarrMobiltv[player]': 'html5',
    'TarrMobiltv[remember]': '1',
    'TarrMobiltv[user]': quote(tarr_user),
    'TarrMobiltv[pass]': quote(tarr_pass),
    'TarrMobiltv[device]': f'{tarr_device_WI}',
    sessioncookie.split("=")[0]: sessioncookie.split("=")[1]
}

headers = {
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0'
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))

    def root(self):
        self.addDirectoryItem("Élő Csatornák", f"get_live_ch", '', 'DefaultFolder.png')
        self.addDirectoryItem("Archív TV", f"get_archive_tv", '', 'DefaultFolder.png')
        self.addDirectoryItem("Filmtár", f"get_filmtar", '', 'DefaultFolder.png')
        self.endDirectory()

    def GetFilmboxMovieCategorys(self, movie_categ_id, movie_categ_name):
        categorys = [
          {"movie_categ_id": 3, "movie_categ_name": "Akció"},
          {"movie_categ_id": 8, "movie_categ_name": "Vígjáték"},
          {"movie_categ_id": 6, "movie_categ_name": "Animációs"},
          {"movie_categ_id": 14, "movie_categ_name": "Családi"},
          {"movie_categ_id": 16, "movie_categ_name": "Kaland"},
          {"movie_categ_id": 4, "movie_categ_name": "Romantikus"},
          {"movie_categ_id": 17, "movie_categ_name": "Sci-Fi"},
          {"movie_categ_id": 10, "movie_categ_name": "Horror"},
          {"movie_categ_id": 5, "movie_categ_name": "Thriller"},
          {"movie_categ_id": 49, "movie_categ_name": "Rémregény"},
          {"movie_categ_id": 12, "movie_categ_name": "Krimi"},
          {"movie_categ_id": 18, "movie_categ_name": "Háborús"},
          {"movie_categ_id": 15, "movie_categ_name": "Dráma"},
          {"movie_categ_id": 19, "movie_categ_name": "Történelmi"},
          {"movie_categ_id": 31, "movie_categ_name": "Dokumentum"},
          {"movie_categ_id": 44, "movie_categ_name": "Sport"},
          {"movie_categ_id": 30, "movie_categ_name": "Docubox"}
        ]
        
        for stuffs in categorys:
            movie_categ_id = int(stuffs['movie_categ_id'])
            movie_categ_name = stuffs['movie_categ_name']
            
            self.addDirectoryItem(f'[B]{movie_categ_name}[/B]', f'get_filmtar_filmbox&movie_categ_id={movie_categ_id}&movie_categ_name={movie_categ_name}', '', 'DefaultMovies.png', isFolder=True, meta={'title': movie_categ_name})

        self.endDirectory('series')

    def GetLiveCh(self, channel_num, title, channel_logo, next_title, channel_current_length):
        
        data_s = requests.post(f'{base_url}/ajax/broadcast/getchannellist/', headers=headers, cookies=cookies).json()

        extracted_data = []
        for ch_num, channel_info in data_s['channels'].items():
            channel_num = int(ch_num)

            ch_name = channel_info['name']
            channel_name = re.sub(r'[+]', r'#', ch_name)
            channel_logo = channel_info['logo']

            channel_current_id = channel_info['showtimes']['current']['id']
            channel_current_start = channel_info['showtimes']['current']['start']['string']
            channel_current_end = channel_info['showtimes']['current']['end']['string']
            channel_current_title = channel_info['showtimes']['current']['title']
            channel_current_length = int(channel_info['showtimes']['current']['length'])

            channel_next_id = channel_info['showtimes']['next']['id']
            channel_next_start = channel_info['showtimes']['next']['start']['string']
            channel_next_end = channel_info['showtimes']['next']['end']['string']
            channel_next_title = channel_info['showtimes']['next']['title']
            channel_next_length = channel_info['showtimes']['next']['length']
            
            title = f'{channel_name} - {channel_current_start}-{channel_current_end} # {channel_current_title}'
            
            next_title = f'Következő: {channel_next_start}-{channel_next_end} # {channel_next_title}'

            self.addDirectoryItem(f'[B]{title}[/B]', f'extr_live_ch&channel_num={channel_num}&title={title}&channel_logo={channel_logo}&next_title={next_title}&channel_current_length={channel_current_length}', channel_logo, 'DefaultMovies.png', isFolder=True, meta={'title': title, 'plot': f'{title}\n{next_title}', 'duration': channel_current_length})
        
        self.endDirectory('series')

    def ExtrLiveCh(self, channel_num, title, channel_logo, url, next_title, channel_current_length):
        
        response_1 = requests.post(f'{base_url}/ajax/broadcast/sessionurl/', cookies=cookies, headers=headers).json()
        
        session_URL = response_1['sessionURL']
        session_URL = re.sub(r'channel_id=(\d+)', fr'channel_id={channel_num}', session_URL)

        response_2 = requests.get(session_URL, cookies=cookies, headers=headers).json()
        m3u8_url = response_2['url']

        self.addDirectoryItem(f'[B]{title}[/B]', f'play_movie&url={quote_plus(m3u8_url)}&title={title}&channel_logo={channel_logo}', channel_logo, 'DefaultMovies.png', isFolder=False, meta={'title': title, 'plot': f'{title}\n{next_title}', 'duration': channel_current_length})

        self.endDirectory('series')



    def GetArchiveTv(self, channel_num, title, channel_logo):        
        archiv_channels = [
          {
            "archiv_channel_id": 354,
            "archiv_channel_title": "Film4 HD",
            "archiv_channel_logo": "https://apiv2.mobiltv.tarr.hu/images/channellogos/v2/film4-dark.png"
          },
          {
            "archiv_channel_id": 353,
            "archiv_channel_title": "Story4 HD",
            "archiv_channel_logo": "https://apiv2.mobiltv.tarr.hu/images/channellogos/v2/story4-dark.png"
          },
          {
            "archiv_channel_id": 9293,
            "archiv_channel_title": "Galaxy4 HD",
            "archiv_channel_logo": "https://apiv2.mobiltv.tarr.hu/images/channellogos/v2/galaxy4-dark.png"
          },
          {
            "archiv_channel_id": 352,
            "archiv_channel_title": "TV4 HD",
            "archiv_channel_logo": "https://apiv2.mobiltv.tarr.hu/images/channellogos/v2/tv4-dark.png"
          }
        ]

        for channel in archiv_channels:
            
            channel_num = int(channel["archiv_channel_id"])
            title = channel["archiv_channel_title"]
            channel_logo = channel["archiv_channel_logo"]
            
            self.addDirectoryItem(f'[B]{title}[/B]', f'extr_archive_tv&channel_num={channel_num}&title={title}&channel_logo={channel_logo}', channel_logo, 'DefaultMovies.png', isFolder=True, meta={'title': title})

        self.endDirectory('series')

    def ExtrArchiveTv(self, channel_num, title, channel_logo, class_picture, class_time_text, class_run_time_seconds, jump_to_show_data_id, data_name): 
        
        data = {
            'channel': f'{channel_num}',
            'page': '1',
            'perPage': '99',
            'ajaxContent': '1',
        }
        
        response = requests.post(f'{base_url}/catchup/showlist', cookies=cookies, headers=headers, data=data)
        
        default_picture_link = f"{base_url}/images/player-poster.jpg"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        shows = soup.find_all('div', class_='show catchup')
        
        for show in shows:
            picture_div = show.find('div', class_='picture')
            class_picture = picture_div.img['src'] if picture_div and picture_div.img else default_picture_link
            if not class_picture.startswith("http"):
                class_picture = default_picture_link
            
            time_div = show.find('div', class_='time')
            class_time_text = time_div.contents[0].strip() if time_div else ""
            
            class_run_time = show.find('div', class_='run-time').text.strip()
            class_run_time_seconds = int(class_run_time.split()[0]) * 60
            
            jump_to_show_data_id = int(show.find('div', class_='nav').find('div', class_='tiny-button jump-to-show')['data-id'])
            data_showtime_id = show['data-id']
            data_name = show.find('div', class_='tiny-button')['data-name']
        
            self.addDirectoryItem(f'[B]{class_time_text} # {data_name}[/B]', f'extr_archive_hls&title={title}&channel_logo={channel_logo}&class_picture={class_picture}&class_time_text={class_time_text}&class_run_time_seconds={class_run_time_seconds}&jump_to_show_data_id={jump_to_show_data_id}&data_name={data_name}', class_picture, 'DefaultMovies.png', isFolder=True, meta={'title': title, 'plot': f'{title} # {class_time_text} # {data_name}', 'duration': class_run_time_seconds})

        self.endDirectory('series')

    def ExtrArchiveHls(self, channel_num, title, channel_logo, class_picture, class_time_text, class_run_time_seconds, jump_to_show_data_id, data_name):
        
        response_1 = requests.post(f'{base_url}/ajax/catchup/sessionurl/', cookies=cookies, headers=headers).json()
        
        session_URL = response_1['sessionURL']
        session_URL = re.sub(r'showtimeId=(\d+)', fr'showtimeId={jump_to_show_data_id}', session_URL)

        response_2 = requests.get(session_URL, cookies=cookies, headers=headers).json()
        m3u8_url = response_2['url']

        self.addDirectoryItem(f'[B]{class_time_text} # {data_name}[/B]', f'play_movie&url={quote_plus(m3u8_url)}&title={title}&channel_logo={channel_logo}&class_picture={class_picture}&class_time_text={class_time_text}&class_run_time_seconds={class_run_time_seconds}&jump_to_show_data_id={jump_to_show_data_id}&data_name={data_name}', class_picture, 'DefaultMovies.png', isFolder=False, meta={'title': f'{class_time_text} # {data_name}', 'plot': f'{title} # {class_time_text} # {data_name}', 'duration': class_run_time_seconds})

        self.endDirectory('series')



    def GetFilmTar(self):
        epic_logo = 'https://apiv2.mobiltv.tarr.hu/images/channellogos/v2/vod/epic-drama.png'
        filmbox_logo = 'https://apiv2.mobiltv.tarr.hu/images/channellogos/v2/vod/hires/filmbox-on-demand.png'
        
        self.addDirectoryItem(f'[B]Epic Drama[/B]', f'get_filmtar_epic', epic_logo, 'DefaultMovies.png', isFolder=True)
        self.addDirectoryItem(f'[B]Filmbox on Demand[/B]', f'get_filmbox_movie_category', filmbox_logo, 'DefaultMovies.png', isFolder=True)

        self.endDirectory('series')


    def GetFilmtarEpic(self, cleaned_title, type_tag, release_year, data_show_id, img_src):
        
        data = {
            'group': '3',
            'category': '0',
            'page': '1',
            'perPage': '99',
            'search': '',
            'ajaxContent': '1',
        }
        
        response = requests.post(f'{base_url}/vod/showlist', cookies=cookies, headers=headers, data=data)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        shows = soup.find_all('div', class_='show')
        
        pattern = r"\s+-\s*[sS]\d{1,2}e\d{1,3}$"
        
        for show in shows:
            type_tag = show.find('div', class_='type-tag').text.strip()
            title = show.find('div', class_='title').find('h5').text.strip()
            img_src = show.find('div', class_='centered').find('img')['src']
            release_year = show.find('div', class_='year-time').find_all('i')[0].next_sibling.strip()
            data_show_id = int(show['data-show-id'])
        
            cleaned_title = re.sub(pattern, "", title)
            
            self.addDirectoryItem(f'[B]{cleaned_title} {release_year} - ({type_tag}) [/B]', f'extr_filmtar_epic&cleaned_title={cleaned_title}&type_tag={type_tag}&release_year={release_year}&data_show_id={data_show_id}&img_src={img_src}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': f'[B]{cleaned_title} {release_year} - ({type_tag}) [/B]', 'plot': f'[B]{cleaned_title} {release_year} - ({type_tag}) [/B]'})

        self.endDirectory('series')

    def ExtrFilmtarEpic(self, cleaned_title, type_tag, release_year, data_show_id, img_src, epic_episode_id, epic_episode_title, epic_current_season):
        
        data = {
            'vodId': data_show_id,
            'ajaxContent': '1',
        }
        
        response = requests.post(f'{base_url}/vod/showtimeinfo', cookies=cookies, headers=headers, data=data)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        seasons = soup.select('select.seasons option')
        episodes = soup.select('select.episodes')

        data = []
        for season in seasons:
            epic_current_season = season.text.strip()
            episodes_for_season = soup.select(f'select.episodes[data-id="{season["value"]}"] option')
            for episode in episodes_for_season:
                epic_episode_id = int(episode['value'])
                epic_episode_title = episode.text.strip()

                self.addDirectoryItem(f'[B]{cleaned_title} - {epic_current_season} {epic_episode_title}[/B]', f'extr_filmtar_epic_hls&cleaned_title={cleaned_title}&type_tag={type_tag}&release_year={release_year}&data_show_id={data_show_id}&img_src={img_src}&epic_episode_id={epic_episode_id}&epic_episode_title={epic_episode_title}&epic_current_season={epic_current_season}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': f'[B]{cleaned_title} - {epic_current_season} {epic_episode_title}[/B]', 'plot': f'[B]{cleaned_title} - {epic_current_season} {epic_episode_title}\n({type_tag}) [/B]'})

        self.endDirectory('series')

    def ExtrFilmtarEpicHls(self, cleaned_title, type_tag, release_year, data_show_id, img_src, epic_episode_id, epic_episode_title, epic_current_season):
        
        response_1 = requests.post(f'{base_url}/ajax/vod/sessionurl/', cookies=cookies, headers=headers).json()
        
        session_URL = response_1['sessionURL']
        session_URL = re.sub(r'vodId=(\d+)', fr'vodId={epic_episode_id}', session_URL)

        response_2 = requests.get(session_URL, cookies=cookies, headers=headers).json()
        m3u8_url = response_2['url']

        self.addDirectoryItem(f'[B]{cleaned_title} - {epic_current_season} {epic_episode_title}[/B]', f'play_movie&url={quote_plus(m3u8_url)}&cleaned_title={cleaned_title}&type_tag={type_tag}&release_year={release_year}&data_show_id={data_show_id}&img_src={img_src}&epic_episode_id={epic_episode_id}&epic_episode_title={epic_episode_title}&epic_current_season={epic_current_season}', img_src, 'DefaultMovies.png', isFolder=False, meta={'title': f'[B]{cleaned_title} - {epic_current_season} {epic_episode_title}[/B]', 'plot': f'[B]{cleaned_title} - {epic_current_season} {epic_episode_title}\n({type_tag}) [/B]'})

        self.endDirectory('series')



    def GetFilmtarFilmbox(self, movie_categ_id, title, release_year, data_show_id, img_src):
        
        data = {
            'group': '0',
            'category': movie_categ_id,
            'page': '1',
            'perPage': '12',
            'search': '',
            'ajaxContent': '1',
        }
        
        response = requests.post(f'{base_url}/vod/showlist', cookies=cookies, headers=headers, data=data)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        shows = soup.find_all('div', class_='show')
        
        for show in shows:
            title = show.find('div', class_='title').find('h5').text.strip()
            img_src = show.find('div', class_='centered').find('img')['src']
            release_year = show.find('div', class_='year-time').find_all('i')[0].next_sibling.strip()
            data_show_id = int(show['data-show-id'])
            
            self.addDirectoryItem(f'[B]{title} ({release_year})[/B]', f'extr_filmtar_filmbox&title={title}&release_year={release_year}&data_show_id={data_show_id}&img_src={img_src}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': f'[B]{title} ({release_year})[/B]', 'plot': f'[B]{title} ({release_year})[/B]'})

        self.endDirectory('movies')        

    def ExtrFilmtarFilmbox(self, movie_categ_id, title, release_year, data_show_id, img_src, description):
        
        data = {
            'vodId': data_show_id,
            'ajaxContent': '1',
        }
        
        response = requests.post(f'{base_url}/vod/showtimeinfo', cookies=cookies, headers=headers, data=data)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        highlight_div = soup.find('div', class_='highlight')
        description = highlight_div.span.text.strip()

        self.addDirectoryItem(f'[B]{title} ({release_year})[/B]', f'extr_filmtar_filmbox_hls&title={title}&release_year={release_year}&data_show_id={data_show_id}&img_src={img_src}&description={description}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': f'[B]{title} ({release_year})[/B]', 'plot': f'{description}'})

        self.endDirectory('series')

    def ExtrFilmtarFilmboxHls(self, movie_categ_id, title, release_year, data_show_id, img_src, description):
        
        response_1 = requests.post(f'{base_url}/ajax/vod/sessionurl/', cookies=cookies, headers=headers).json()
        
        session_URL = response_1['sessionURL']
        session_URL = re.sub(r'vodId=(\d+)', fr'vodId={data_show_id}', session_URL)

        response_2 = requests.get(session_URL, cookies=cookies, headers=headers).json()
        m3u8_url = response_2['url']

        self.addDirectoryItem(f'[B]{title} - {release_year}[/B]', f'play_movie&url={quote_plus(m3u8_url)}&title={title}&release_year={release_year}&data_show_id={data_show_id}&img_src={img_src}&description={description}', img_src, 'DefaultMovies.png', isFolder=False, meta={'title': f'[B]{title} - {release_year}[/B]', 'plot': f'{description}'})

        self.endDirectory('series')

    def playMovie(self, url):
        xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | playMovie | url | {url}', xbmc.LOGINFO)
        
        try:
            play_item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
        except:
            xbmc.log(f'TarrMobiltv | v{version} | Kodi: {kodi_version[:5]} | playMovie | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("TarrMobiltv", "Törölt tartalom", time=5000)

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)
