# -*- coding: utf-8 -*-

'''
    TarrMobiltv Addon
    Copyright (C) 2024 heg

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
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

channel_num = params.get('channel_num')
title = params.get('title')
channel_logo = params.get('channel_logo')
next_title = params.get('next_title')
channel_current_length = params.get('channel_current_length')

class_picture = params.get('class_picture')
class_time_text = params.get('class_time_text')
class_run_time_seconds = params.get('class_run_time_seconds')
jump_to_show_data_id = params.get('jump_to_show_data_id')
data_name = params.get('data_name')

cleaned_title = params.get('cleaned_title')
type_tag = params.get('type_tag')
release_year = params.get('release_year')
data_show_id = params.get('data_show_id')
img_src = params.get('img_src')
epic_episode_id = params.get('epic_episode_id')
epic_episode_title = params.get('epic_episode_title')
epic_current_season = params.get('epic_current_season')

movie_categ_id = params.get('movie_categ_id')
movie_categ_name = params.get('movie_categ_name')


description = params.get('description')


if action is None:
    navigator.navigator().root()

elif action == 'get_live_ch':
    navigator.navigator().GetLiveCh(channel_num, title, channel_logo, next_title, channel_current_length)

elif action == 'extr_live_ch':
    navigator.navigator().ExtrLiveCh(channel_num, title, channel_logo, url, next_title, channel_current_length)



elif action == 'get_archive_tv':
    navigator.navigator().GetArchiveTv(channel_num, title, channel_logo)

elif action == 'extr_archive_tv':
    navigator.navigator().ExtrArchiveTv(channel_num, title, channel_logo, class_picture, class_time_text, class_run_time_seconds, jump_to_show_data_id, data_name)

elif action == 'extr_archive_hls':
    navigator.navigator().ExtrArchiveHls(channel_num, title, channel_logo, class_picture, class_time_text, class_run_time_seconds, jump_to_show_data_id, data_name)



elif action == 'get_filmtar':
    navigator.navigator().GetFilmTar()



elif action == 'get_filmtar_epic':
    navigator.navigator().GetFilmtarEpic(cleaned_title, type_tag, release_year, data_show_id, img_src)

elif action == 'extr_filmtar_epic':
    navigator.navigator().ExtrFilmtarEpic(cleaned_title, type_tag, release_year, data_show_id, img_src, epic_episode_id, epic_episode_title, epic_current_season)

elif action == 'extr_filmtar_epic_hls':
    navigator.navigator().ExtrFilmtarEpicHls(cleaned_title, type_tag, release_year, data_show_id, img_src, epic_episode_id, epic_episode_title, epic_current_season)



elif action == 'get_filmbox_movie_category':
    navigator.navigator().GetFilmboxMovieCategorys(movie_categ_id, movie_categ_name)

elif action == 'get_filmtar_filmbox':
    navigator.navigator().GetFilmtarFilmbox(movie_categ_id, title, release_year, data_show_id, img_src)

elif action == 'extr_filmtar_filmbox':
    navigator.navigator().ExtrFilmtarFilmbox(movie_categ_id, title, release_year, data_show_id, img_src, description)

elif action == 'extr_filmtar_filmbox_hls':
    navigator.navigator().ExtrFilmtarFilmboxHls(movie_categ_id, title, release_year, data_show_id, img_src, description)



elif action == 'play_movie':
    navigator.navigator().playMovie(url)