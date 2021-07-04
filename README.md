# RPDB-Media-Agent.bundle

RPDB Plug-in for Plex; Adds Posters / Backgrounds with Ratings from [RPDB](https://ratingposterdb.com/)

## Install

- [Download Plug-in](https://github.com/RatingPosterDB/RPDB-Media-Agent.bundle/releases/download/v0.0.5/RPDB-Media-Agent.bundle.zip)
- Copy Contents of Plug-in to Plex's "Plug-ins" Folder
- Restart Plex
- In Plex, go to Account > Agents (under "Settings")
- Select an Agent that has "Rating Poster Database" Available (for example: Shows > The Movie Database)
- Press the Gear Icon to the Right of the Plug-in
- Enter [RPDB API Key](https://ratingposterdb.com/api-key/) and Choose Settings
- Click "Save"
- Move the "Rating Poster Database" Plug-in to the Top of ALL Agents (for "Shows", move it to the top of both "TheTVDB" and also "The Movie Database", for "Movies" move it to the top of both "The Movie Database" and "Plex Movie (Legacy)", it is very important that this plug-in is the first in all lists in order for it to function properly)

## Important Note

This plug-in will work as expected for absolutely all Media Agents EXCEPT the default "Plex Movie" and "Plex TV Series" agents.

You can change the default Media Agent for a library by going to Account > Libraries (under "Manage") > Edit (right side of a library line) > Advanced > Agent.

You need to ensure that any other Media Agent is used for Movies instead of the "Plex Movie" entitled Agent, and for Series any other Media Agent except "Plex TV Series".

**The fact that it won't work with the default "Plex Movie" and "Plex TV Series" agents is a limitation in Plex's architecture and cannot be fixed within the plug-in.**

If you wish to still use the "Plex Movie" and "Plex TV Series" default agents, then I suggest using the [RPDB Folders](https://github.com/RatingPosterDB/rpdb-folders/blob/main/README.md) application instead of this plug-in, which will work with any agent, including many other applications. (RPDB Folders was tested with: Plex, Emby, Jellyfin and Kodi)
