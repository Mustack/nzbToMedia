import logging
import urllib

from lib import requests

from nzbToMediaConfig import config

def autoFork(section, inputCategory):

    Logger = logging.getLogger()

    # config settings
    try:
        host = config()[section][inputCategory]["host"]
        port = config()[section][inputCategory]["port"]
    except:
        host = None
        port = None

    try:
        username = config()[section][inputCategory]["username"]
        password = config()[section][inputCategory]["password"]
    except:
        username = None
        password = None

    try:
        ssl = int(config()[section][inputCategory]["ssl"])
    except (config, ValueError):
        ssl = 0

    try:
        web_root = config()[section][inputCategory]["web_root"]
    except config:
        web_root = ""

    try:
        fork = config.FORKS.items()[config.FORKS.keys().index(config()[section][inputCategory]["fork"])]
    except:
        fork = "auto"

    if ssl:
        protocol = "https://"
    else:
        protocol = "http://"

    detected = False
    if fork == "auto":
        Logger.info("Attempting to auto-detect " + section + " fork")
        for fork in sorted(config.FORKS.iteritems()):
            url = protocol + host + ":" + port + web_root + "/home/postprocess/processEpisode?" + urllib.urlencode(fork[1])

            # attempting to auto-detect fork
            try:
                if username and password:
                    r = requests.get(url, auth=(username, password))
                else:
                    r = requests.get(url)
            except requests.ConnectionError:
                Logger.info("Could not connect to " + section + ":" + inputCategory + " to perform auto-fork detection!")
                break

            if r.ok:
                detected = True
                break

        if detected:
            Logger.info("" + section + ":" + inputCategory + " fork auto-detection successful ...")
        else:
            Logger.info("" + section + ":" + inputCategory + " fork auto-detection failed")
            fork = config.FORKS.items()[config.FORKS.keys().index(config.FORK_DEFAULT)]

    Logger.info("" + section + ":" + inputCategory + " fork set to %s", fork[0])
    return fork[0], fork[1]