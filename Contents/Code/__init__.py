import certifi
import requests
import re
import os
from plex_media import media_to_videos

PLUGIN_VERSION = '0.98'

HTTP_HEADERS = {
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12.4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30",
  "Referer": "https://ratingposterdb.com/"
}

POSTER_TYPE_MAP = {
    "Ratings": "poster-default",
    "Ratings + Certification": "poster-certs",
    "IMDB + RT + RT Audience": "poster-rt",
    "IMDB + MC + MC Audience": "poster-mc"
}

imdb_guid_identifier = "com.plexapp.agents.imdb://"
tvdb_guid_identifier = "com.plexapp.agents.thetvdb://"
tmdb_guid_identifier = "com.plexapp.agents.themoviedb://"


####################################################################################################

def Start():
  pass

def ValidatePrefs():
  pass

####################################################################################################

# :: MOVIES AGENT # com_plexapp_agents_themoviedb
class RpdbApiAgent(object):
	languages = [Locale.Language.NoLanguage]
	primary_provider = False

	def __init__(self, *args, **kwargs):
		super(RpdbApiAgent, self).__init__(*args, **kwargs)
		self.agent_type = "movies" if isinstance(self, Agent.Movies) else "series"
		if isinstance(self, Agent.Movies):
			self.contributes_to = [
				'com.plexapp.agents.imdb',
				'com.plexapp.agents.themoviedb',
			]
		else:
			self.contributes_to = [
				'com.plexapp.agents.imdb',
				'com.plexapp.agents.themoviedb',
			    'com.plexapp.agents.thetvdb'
			]
		self.name = "Rating Poster Database (%s, %s)" % (self.agent_type_verbose, PLUGIN_VERSION)

	def search(self, results, media, lang):
		Log.Debug(':: RPDB (%s) STARTED ::' % self.agent_type)
		if media.primary_metadata is not None:
			results.Append(MetadataSearchResult(
				id = media.primary_metadata.id,
				score = 100
			))

	def update(self, metadata, media, lang):
		# PROCESS TITLE

		title = str(media.title)

		valid_names 	= list()
		foundPosters 	= []

		Log.Debug(':: SEARCHING POSTERS FOR :: %s' % title)
		# -----------------------------------------------------

		poster_source = None
		poster_id = None

		if imdb_guid_identifier in media.guid:
			poster_source = 'imdb'
			poster_id = media.guid[len(imdb_guid_identifier):].split("?")[0]
		if tmdb_guid_identifier in media.guid:
			poster_source = 'tmdb'
			if self.agent_type == 'movies':
				poster_media_type = 'movie'
			else:
				poster_media_type = 'series'
			poster_id = '{}-{}'.format(poster_media_type,media.guid[len(tmdb_guid_identifier):].split("?")[0])
		if tvdb_guid_identifier in media.guid:
			poster_source = 'tvdb'
			poster_id = media.guid[len(tvdb_guid_identifier):].split("?")[0]

		if poster_id is not None:

			poster_type = POSTER_TYPE_MAP[Prefs['poster_type']]
			low_rpdb_key = False

			if Prefs['rpdb_key'].startswith("t1-") or Prefs['rpdb_key'].startswith("t2-"):
				low_rpdb_key = True

			if Prefs['textless']:
				poster_type = poster_type.replace('poster-', 'textless-')

			poster_url = 'https://api.ratingposterdb.com/{}/{}/{}/{}.jpg'.format(Prefs['rpdb_key'],poster_source,poster_type,poster_id)

			querystring = '?'

			if not Prefs['rpdb_key'].startswith("t1-"):
				poster_lang = re.findall("\(([a-z]{2})\)$", Prefs['poster_lang'])

				if poster_lang and poster_lang[0] and poster_lang[0] != "en":
					querystring += 'lang={}'.format(poster_lang[0])

			if not low_rpdb_key:
				if (Prefs['movie_resolution_badge'] and self.agent_type == 'movies') or (Prefs['series_resolution_badge'] and self.agent_type == 'series') or (self.agent_type == 'movies' and (Prefs['audio_channels_badge'] or Prefs['encoding_badge'] or Prefs['container_badge'])):
					all_videos = media_to_videos(media, kind=self.agent_type)
					if all_videos[0]:
						badges = ''
						Log.Debug(all_videos[0])
						if all_videos[0]['stream']:
							if (Prefs['movie_resolution_badge'] and self.agent_type == 'movies') or (Prefs['series_resolution_badge'] and self.agent_type == 'series'):
								if all_videos[0]['stream']['resolution']:
									if all_videos[0]['stream']['resolution'] in ['240p','360p','480p','720p','1080p']:
										badges += all_videos[0]['stream']['resolution']
									elif all_videos[0]['stream']['resolution'] in ['1440p', '2kp']:
										badges += '2k'
									elif all_videos[0]['stream']['resolution'] in ['2160p', '4kp']:
										badges += '4k'
									elif all_videos[0]['stream']['resolution'] in ['2880p', '5kp']:
										badges += '5k'
									elif all_videos[0]['stream']['resolution'] in ['4320p', '8kp']:
										badges += '8k'
									elif all_videos[0]['stream']['resolution'] in ['fullhdp', 'full hdp']:
										badges += '1080p'
									elif all_videos[0]['stream']['resolution'] in ['hdp']:
										badges += '720p'
									elif all_videos[0]['stream']['resolution'] in ['sdp']:
										badges += 'sd'

							if Prefs['audio_channels_badge'] and self.agent_type == 'movies':
								if all_videos[0]['stream']['audio_channels'] in ['2.0','5.1','7.1']:
									if len(badges) > 0:
										badges += '%2C'
									badges += 'audio{}'.format(all_videos[0]['stream']['audio_channels'].replace(".", ""))

							if Prefs['encoding_badge'] and self.agent_type == 'movies':
								if all_videos[0]['stream']['video_codec'].lower() in ['h264', 'x264', 'avc']:
									if len(badges) > 0:
										badges += '%2C'
									badges += 'h264'
								if all_videos[0]['stream']['video_codec'].lower() in ['h265', 'x265', 'hevc']:
									if len(badges) > 0:
										badges += '%2C'
									badges += 'h265'

						if Prefs['container_badge'] and self.agent_type == 'movies':
							filename, file_extension = os.path.splitext(all_videos[0]['plex_part'].file)
							if file_extension.lower() in ['.mkv', '.mp4', '.avi']:
								if len(badges) > 0:
									badges += '%2C'
								badges += file_extension.replace(".", "").lower()

						if len(badges) > 0:
							if len(querystring) > 1:
								querystring += '&'
							if Prefs['badge_position'] != 'Left':
								querystring += 'badgePos={}&badges={}'.format(Prefs['badge_position'].lower(), badges)
							else:
								querystring += 'badges={}'.format(badges)

			if len(querystring) > 1:
				poster_url += querystring

			Log.Debug(':: POSTER URL :: %s' % poster_url)

			if poster_url not in metadata.posters.keys():

				poster_sort = 1000 - len(metadata.posters.keys())

				valid_names = metadata.posters.keys()

				r = requests.get(poster_url, headers=HTTP_HEADERS, verify=certifi.where())

				if r.status_code == 200:

					valid_names.insert(0, poster_url)
					metadata.posters[poster_url] = Proxy.Media(r.content, sort_order=poster_sort)
					metadata.posters.validate_keys(valid_names)

			if Prefs['backdrops'] and not low_rpdb_key:
				backdrop_url = 'https://api.ratingposterdb.com/{}/{}/backdrop-default/{}.jpg'.format(Prefs['rpdb_key'],poster_source,poster_id)

				if backdrop_url not in metadata.art.keys():

					backdrop_sort = 1000 - len(metadata.art.keys())

					backdrop_valid_names = metadata.art.keys()

					rb = requests.get(backdrop_url, headers=HTTP_HEADERS, verify=certifi.where())

					if rb.status_code == 200:

						backdrop_valid_names.insert(0, backdrop_url)
						metadata.art[backdrop_url] = Proxy.Media(rb.content, sort_order=backdrop_sort)
						metadata.art.validate_keys(backdrop_valid_names)


####################################################################################################

# REGISTER AGENTS
class RpdbApiMovies(RpdbApiAgent, Agent.Movies):
	agent_type_verbose = "Movies"

class RpdbApiTvShows(RpdbApiAgent, Agent.TV_Shows):
	agent_type_verbose = "TV"
