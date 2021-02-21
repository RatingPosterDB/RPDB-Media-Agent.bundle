# RPDB-Media-Agent.bundle

[RPDB](https://ratingposterdb.com/) Plug-in for Plex; Adds Posters / Backgrounds with Ratings

## Install

- [Download Plug-in](https://github.com/jaruba/RPDB-Media-Agent.bundle/releases/download/v0.0.1/RPDB-Media-Agent.bundle.zip)
- Copy Contents of Plug-in to Plex's "Plug-ins" Folder
- Restart Plex
- In Plex, go to Account > Agents (under "Settings")
- Select an Agent that has "Rating Poster Database" Available (for example: Shows > The Movie Database)
- Press the Gear Icon to the Right of the Plug-in
- Enter [RPDB API Key](https://ratingposterdb.com/api-key/) and Choose Settings
- Click "Save"
- Move the "Rating Poster Database" Plug-in to the Top of ALL Agents (for "Shows", move it to the top of both "TheTVDB" and also "The Movie Database", for "Movies" move it to the top of both "The Movie Database" and "Plex Movie (Legacy)", it is very important that this plug-in is the first in all lists in order for it to function properly)

## Important Note

This plug-in will work as expected for absolutely all Media Agents EXCEPT the new default "Plex Movie" agent (that is used by default for movies only).

You can change the default Media Agent for a library by going to Account > Libraries (under "Manage") > Edit (right side of a library line) > Advanced > Agent.

It will work as expected by default with Series, but in order for it to also work with movies, you need to ensure that any other Media Agent is used for Movies instead of the "Plex Movie" entitled Agent.

The fact that it won't work with the default "Plex Movie" agent is a limitation in Plex's architecture and cannot be fixed within the plug-in.

If you wish to still use the "Plex Movie" default agent, then I suggest using the [RPDB Folders](https://github.com/jaruba/rpdb-folders/blob/main/README.md) application instead of this plug-in, which will work with any agent, including many other applications. (RPDB Folders was tested with: Plex, Emby, Kodi)
