# coding=utf-8

from socket import timeout
from lib import Plex

def get_item(key):
    try:
        item_id = int(key)
    except ValueError:
        return

    try:
        item_container = Plex["library"].metadata(item_id)
    except timeout:
        Log.Debug("PMS API timed out when querying information about item %d", item_id)
        return

    try:
        return list(item_container)[0]
    except:
        pass
