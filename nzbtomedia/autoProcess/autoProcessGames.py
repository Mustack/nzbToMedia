import json
import nzbtomedia
from lib import requests
from nzbtomedia.nzbToMediaUtil import convert_to_ascii
from nzbtomedia import logger

class autoProcessGames:
    def process(self, dirName, nzbName=None, status=0, clientAgent='manual', inputCategory=None):
        if dirName is None:
            logger.error("No directory was given!")
            return 1  # failure

        # auto-detect correct section
        section = nzbtomedia.CFG.findsection(inputCategory)
        if not section:
            logger.error(
                "We were unable to find a section for category %s, please check your autoProcessMedia.cfg file.", inputCategory)
            return 1

        logger.postprocess("Loading config from %s", nzbtomedia.CONFIG_FILE)

        status = int(status)

        host = nzbtomedia.CFG[section][inputCategory]["host"]
        port = nzbtomedia.CFG[section][inputCategory]["port"]
        apikey = nzbtomedia.CFG[section][inputCategory]["apikey"]

        try:
            ssl = int(nzbtomedia.CFG[section][inputCategory]["ssl"])
        except:
            ssl = 0

        try:
            web_root = nzbtomedia.CFG[section][inputCategory]["web_root"]
        except:
            web_root = ""

        if ssl:
            protocol = "https://"
        else:
            protocol = "http://"

        nzbName, dirName = convert_to_ascii(nzbName, dirName)

        baseURL = protocol + host + ":" + port + web_root + "/api?api_key=" + apikey + "&mode="

        fields = nzbName.split("-")
        gamezID = fields[0].replace("[","").replace("]","").replace(" ","")
        downloadStatus = 'Wanted'
        if status == 0:
            downloadStatus = 'Downloaded'

        url = baseURL + "UPDATEREQUESTEDSTATUS&db_id=" + gamezID + "&status=" + downloadStatus

        logger.debug("Opening URL: %s", url)

        try:
            r = requests.get(url, stream=True)
        except requests.ConnectionError:
            logger.error("Unable to open URL")
            return 1  # failure

        result = {}
        for line in r.iter_lines():
            if line:
                logger.postprocess("%s", line)
                result.update(json.load(line))

        if result['success']:
            logger.postprocess("Status for %s has been set to %s in Gamez", gamezID, downloadStatus)
            return 0 # Success
        else:
            logger.error("Status for %s has NOT been updated in Gamez", gamezID)
            return 1 # failure
