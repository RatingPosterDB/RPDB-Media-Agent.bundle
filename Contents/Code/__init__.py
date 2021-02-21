import certifi
import requests

PLUGIN_VERSION = '0.95'

HTTP_HEADERS = {
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12.4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30",
  "Referer": "https://ratingposterdb.com/"
}

POSTER_TYPE_MAP = {
    "Ratings": "poster-default",
    "Ratings + Certifications": "poster-certs",
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
		self.agent_type = "MOVIES" if isinstance(self, Agent.Movies) else "SERIES"
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
		#processTitle(str(media.title))
		Log.Debug('update 1111')
		# PROCESS TITLE
		Log.Debug(media.guid)

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
			poster_id = media.guid[len(tmdb_guid_identifier):].split("?")[0]
		if tvdb_guid_identifier in media.guid:
			poster_source = 'tvdb'
			poster_id = media.guid[len(tvdb_guid_identifier):].split("?")[0]

		if poster_id is not None:

			poster_url = 'https://api.ratingposterdb.com/{}/{}/{}/{}.jpg'.format(Prefs['rpdb_key'],poster_source,POSTER_TYPE_MAP[Prefs['poster_type']],poster_id)

			if poster_url not in metadata.posters:

				r = requests.get(poster_url, headers=HTTP_HEADERS, verify=certifi.where())

				if r.status_code == 200:

					valid_names = list()
					valid_names.append(poster_url)
					metadata.posters[poster_url] = Proxy.Preview(r.content)
					metadata.posters.validate_keys(valid_names)

			if Prefs['backdrops']:
				backdrop_url = 'https://api.ratingposterdb.com/{}/{}/backdrop-default/{}.jpg'.format(Prefs['rpdb_key'],poster_source,poster_id)

				if backdrop_url not in metadata.art:

					rb = requests.get(backdrop_url, headers=HTTP_HEADERS, verify=certifi.where())

					if rb.status_code == 200:

						backdrop_valid_names = list()
						backdrop_valid_names.append(backdrop_url)
						metadata.art[backdrop_url] = Proxy.Preview(rb.content)
						metadata.art.validate_keys(backdrop_valid_names)

# ^ alternatively, to not handle the request outserves:
# metadata.posters[poster] = Proxy.Preview(HTTP.Request(poster), sort_order=i)


####################################################################################################

# REGISTER AGENTS
class RpdbApiMovies(RpdbApiAgent, Agent.Movies):
	contributes_to = [
		'com.plexapp.agents.imdb',
		'com.plexapp.agents.themoviedb'
	]
	agent_type_verbose = "Movies"

class RpdbApiTvShows(RpdbApiAgent, Agent.TV_Shows):
	contributes_to = [
		'com.plexapp.agents.imdb',
		'com.plexapp.agents.themoviedb'
	]
	agent_type_verbose = "TV"
