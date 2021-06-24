# coding=utf-8

from babelfish.exceptions import LanguageError

from subzero.language import Language, language_from_stream
def get_language_from_stream(lang_code):
    if lang_code:
        lang = Locale.Language.Match(lang_code)
        if lang and lang != "xx":
            # Log.Debug("Found language: %r", lang)
            return Language.fromietf(lang)
        elif lang:
            try:
                return language_from_stream(lang_code)
            except LanguageError:
                pass


def get_language(lang_short):
    return Language.fromietf(lang_short)


def display_language(l):
    if not l:
        return "Unknown"
    return _(str(l.basename).lower()) + ((u" (%s)" % _("forced")) if l.forced else "")


class PartUnknownException(Exception):
    pass