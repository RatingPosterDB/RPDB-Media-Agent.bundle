# coding=utf-8

import os

import helpers
from items import get_item
from subzero.language import Language

TEXT_SUBTITLE_EXTS = ("srt", "ass", "ssa", "vtt", "mov_text")

def get_metadata_dict(item, part, add):
    data = {
        "item": item,
        "section": item.section.title,
        "path": part.file,
        "folder": os.path.dirname(part.file),
        "filename": os.path.basename(part.file)
    }
    data.update(add)
    return data


imdb_guid_identifier = "com.plexapp.agents.imdb://"
tvdb_guid_identifier = "com.plexapp.agents.thetvdb://"


def get_plexapi_stream_info(plex_item, part_id=None):
    if not plex_item:
        return

    d = {"stream": {}}
    data = d["stream"]

    # find current part
    current_part = None
    current_media = None
    for media in plex_item.media:
        for part in media.parts:
            if not part_id or str(part.id) == part_id:
                current_part = part
                current_media = media
                break
        if current_part:
            break

    if not current_part:
        return d

    data["video_codec"] = current_media.video_codec
    if current_media.audio_codec:
        data["audio_codec"] = current_media.audio_codec.upper()

        if data["audio_codec"] == "DCA":
            data["audio_codec"] = "DTS"

    if current_media.audio_channels == 8:
        data["audio_channels"] = "7.1"

    elif current_media.audio_channels == 6:
        data["audio_channels"] = "5.1"
    else:
        data["audio_channels"] = "%s.0" % str(current_media.audio_channels)

    if data["audio_channels"] == 'None.0':
        data["audio_channels"] = '2.0'

    # iter streams
    for stream in current_part.streams:
        if stream.stream_type == 1:
            # video stream
            data["resolution"] = "%s%s" % (current_media.video_resolution, "p")
            break

    return d


def media_to_videos(media, kind="series"):
    """
    iterates through media and returns the associated parts (videos)
    :param media:
    :param kind:
    :return:
    """
    videos = []

    # this is a Show or a Movie object
    plex_item = get_item(media.id)
    year = plex_item.year
    original_title = plex_item.title_original

    if kind == "series":
        for season in media.seasons:
            season_object = media.seasons[season]
            for episode in media.seasons[season].episodes:
                ep = media.seasons[season].episodes[episode]

                tvdb_id = None
                series_tvdb_id = None
                if tvdb_guid_identifier in ep.guid:
                    tvdb_id = ep.guid[len(tvdb_guid_identifier):].split("?")[0]
                    series_tvdb_id = tvdb_id.split("/")[0]

                # get plex item via API for additional metadata
                plex_episode = get_item(ep.id)
                stream_info = get_plexapi_stream_info(plex_episode)

                if not stream_info:
                    continue

                for item in media.seasons[season].episodes[episode].items:
                    for part in item.parts:
                        videos.append(
                            get_metadata_dict(plex_episode, part,
                                              dict(stream_info, **{"plex_part": part, "type": "episode",
                                                                    "title": ep.title,
                                                                    "series": media.title, "id": ep.id, "year": year,
                                                                    "series_id": media.id,
                                                                    "super_thumb": plex_item.thumb,
                                                                    "season_id": season_object.id,
                                                                    "imdb_id": None, "series_tvdb_id": series_tvdb_id,
                                                                    "tvdb_id": tvdb_id,
                                                                    "original_title": original_title,
                                                                    "episode": plex_episode.index,
                                                                    "season": plex_episode.season.index,
                                                                    "section": plex_episode.section.title
                                                                    })
                                              )
                        )
    else:
        stream_info = get_plexapi_stream_info(plex_item)

        if stream_info:
            imdb_id = None
            if imdb_guid_identifier in media.guid:
                imdb_id = media.guid[len(imdb_guid_identifier):].split("?")[0]
            for item in media.items:
                for part in item.parts:
                    videos.append(
                        get_metadata_dict(plex_item, part, dict(stream_info, **{"plex_part": part, "type": "movie",
                                                                                 "title": media.title, "id": media.id,
                                                                                 "super_thumb": plex_item.thumb,
                                                                                 "series_id": None, "year": year,
                                                                                 "season_id": None, "imdb_id": imdb_id,
                                                                                 "original_title": original_title,
                                                                                 "series_tvdb_id": None, "tvdb_id": None,
                                                                                 "section": plex_item.section.title})
                                          )
                    )
    return videos


IGNORE_FN = ("subzero.ignore", ".subzero.ignore", ".nosz")


def get_all_parts(plex_item):
    parts = []
    for media in plex_item.media:
        parts += media.parts

    return parts


def is_stream_forced(stream):
    stream_title = getattr(stream, "title", "") or ""
    forced = getattr(stream, "forced", False)
    if not forced and stream_title and "forced" in stream_title.strip().lower():
        forced = True

    return forced


def get_embedded_subtitle_streams(part, requested_language=None, skip_duplicate_unknown=True, skip_unknown=False):
    streams = []
    streams_unknown = []
    all_streams = []
    has_unknown = False
    found_requested_language = False
    for stream in part.streams:
        # subtitle stream
        if stream.stream_type == 3 and not stream.stream_key and stream.codec in TEXT_SUBTITLE_EXTS:
            is_forced = is_stream_forced(stream)
            language = helpers.get_language_from_stream(stream.language_code)
            if language:
                language = Language.rebuild(language, forced=is_forced)

            is_unknown = False
            found_requested_language = requested_language and requested_language == language
            stream_data = None

            if not language:
                language = None
                is_unknown = True
                has_unknown = True
                stream_data = {"stream": stream, "is_unknown": is_unknown, "language": language,
                               "is_forced": is_forced}
                streams_unknown.append(stream_data)

            if not requested_language or found_requested_language:
                stream_data = {"stream": stream, "is_unknown": is_unknown, "language": language,
                               "is_forced": is_forced}
                streams.append(stream_data)

                if found_requested_language:
                    break

            if stream_data:
                all_streams.append(stream_data)

    if requested_language:
        if streams_unknown and not found_requested_language and not skip_unknown:
            streams = streams_unknown
    else:
        streams = all_streams

    return streams


def get_part(plex_item, part_id):
    for media in plex_item.media:
        for part in media.parts:
            if str(part.id) == str(part_id):
                return part


def get_plex_metadata(rating_key, part_id, item_type, plex_item=None):
    """
    uses the Plex 3rd party API accessor to get metadata information

    :param rating_key: movie or episode
    :param part_id:
    :param item_type:
    :return:
    """

    if not plex_item:
        plex_item = get_item(rating_key)

    if not plex_item:
        return

    # find current part
    current_part = get_part(plex_item, part_id)

    if not current_part:
        raise helpers.PartUnknownException("Part unknown")

    stream_info = get_plexapi_stream_info(plex_item, part_id)

    if not stream_info:
        return

    # get normalized metadata
    # fixme: duplicated logic of media_to_videos
    if item_type == "episode":
        tvdb_id = None
        series_tvdb_id = None
        if tvdb_guid_identifier in plex_item.guid:
            tvdb_id = plex_item.guid[len(tvdb_guid_identifier):].split("?")[0]
            series_tvdb_id = tvdb_id.split("/")[0]
        metadata = get_metadata_dict(plex_item, current_part,
                                     dict(stream_info,
                                          **{"plex_part": current_part, "type": "episode", "title": plex_item.title,
                                             "series": plex_item.show.title, "id": plex_item.rating_key,
                                             "series_id": plex_item.show.rating_key,
                                             "season_id": plex_item.season.rating_key,
                                             "imdb_id": None,
                                             "tvdb_id": tvdb_id,
                                             "super_thumb": plex_item.show.thumb,
                                             "series_tvdb_id": series_tvdb_id,
                                             "season": plex_item.season.index,
                                             "episode": plex_item.index
                                             })
                                     )
    else:
        imdb_id = None
        original_title = plex_item.title_original
        if imdb_guid_identifier in plex_item.guid:
            imdb_id = plex_item.guid[len(imdb_guid_identifier):].split("?")[0]
        metadata = get_metadata_dict(plex_item, current_part,
                                     dict(stream_info, **{"plex_part": current_part, "type": "movie",
                                                           "title": plex_item.title, "id": plex_item.rating_key,
                                                           "series_id": None,
                                                           "season_id": None,
                                                           "imdb_id": imdb_id,
                                                           "year": plex_item.year,
                                                           "tvdb_id": None,
                                                           "super_thumb": plex_item.thumb,
                                                           "series_tvdb_id": None,
                                                           "original_title": original_title,
                                                           "season": None,
                                                           "episode": None,
                                                           "section": plex_item.section.title})
                                     )
    return metadata


class PMSMediaProxy(object):
    """
    Proxy object for getting data from a mediatree items "internally" via the PMS

    note: this could be useful later on: Media.TV_Show(getattr(Metadata, "_access_point"), id=XXXXXX)
    """

    def __init__(self, media_id):
        self.mediatree = Media.TreeForDatabaseID(media_id)

    def get_part(self, part_id=None):
        """
        walk the mediatree until the given part was found; if no part was given, return the first one
        :param part_id:
        :return:
        """
        m = self.mediatree
        while 1:
            if m.items:
                media_item = m.items[0]
                if not part_id:
                    return media_item.parts[0] if media_item.parts else None

                for part in media_item.parts:
                    if str(part.id) == str(part_id):
                        return part
                break

            if not m.children:
                break

            m = m.children[0]

    def get_all_parts(self):
        """
        walk the mediatree until the given part was found; if no part was given, return the first one
        :param part_id:
        :return:
        """
        m = self.mediatree
        parts = []
        while 1:
            if m.items:
                media_item = m.items[0]
                for part in media_item.parts:
                    parts.append(part)
                break

            if not m.children:
                break

            m = m.children[0]
        return parts
