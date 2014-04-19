#!/usr/bin/env python
#
##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Post-Process to CouchPotato, SickBeard, NzbDrone, Mylar, Gamez, HeadPhones.
#
# This script sends the download to your automated media management servers.
#
# NOTE: This script requires Python to be installed on your system.

##############################################################################
### OPTIONS                                                                ###

## General

# Auto Update nzbToMedia (0, 1).
#
# Set to 1 if you want nzbToMedia to automatically check for and update to the latest version
#auto_update=0

## CouchPotato

# CouchPotato script category.
#
# category that gets called for post-processing with CouchPotatoServer.
#cpsCategory=movie

# CouchPotato api key.
#cpsapikey=

# CouchPotato host.
#cpshost=localhost

# CouchPotato port.
#cpsport=5050

# CouchPotato uses ssl (0, 1).
#
# Set to 1 if using ssl, else set to 0.
#cpsssl=0

# CouchPotato URL_Base
#
# set this if using a reverse proxy.
#cpsweb_root=

# CouchPotato Postprocess Method (renamer, manage).
#
# use "renamer" for CPS renamer (default) or "manage" to call a manage update.
#cpsmethod=renamer

# CouchPotato Delete Failed Downloads (0, 1).
#
# set to 1 to delete failed, or 0 to leave files in place.
#cpsdelete_failed=0

# CouchPotato wait_for
#
# Set the number of minutes to wait after calling the renamer, to check the movie has changed status.
#cpswait_for=2

# CouchPotatoServer and NZBGet are a different system (0, 1).
#
# set to 1 if CouchPotato and NZBGet are on a different system, or 0 if on the same system.
#remoteCPS = 0

## SickBeard

# SickBeard script category.
#
# category that gets called for post-processing with SickBeard.
#sbCategory=tv

# SickBeard host.
#sbhost=localhost

# SickBeard port.
#sbport=8081

# SickBeard username.
#sbusername=

# SickBeard password.
#sbpassword=

# SickBeard uses ssl (0, 1).
#
# Set to 1 if using ssl, else set to 0.
#sbssl=0

# SickBeard web_root
#
# set this if using a reverse proxy.
#sbweb_root=

# SickBeard watch directory.
#
# set this if SickBeard and nzbGet are on different systems.
#sbwatch_dir=

# SickBeard fork.
#
# set to default or auto to auto-detect the custom fork type.
#sbfork=auto

# SickBeard Delete Failed Downloads (0, 1).
#
# set to 1 to delete failed, or 0 to leave files in place.
#sbdelete_failed=0

# SickBeard process method.
#
# set this to move, copy, hardlin, symlink as appropriate if you want to over-ride SB defaults. Leave blank to use SB default.
#sbprocess_method=

## NzbDrone

# NzbDrone script category.
#
# category that gets called for post-processing with NzbDrone.
#ndCategory=tv

# NzbDrone host.
#ndhost=localhost

# NzbDrone port.
#ndport=8989

# NzbDrone API key.
#ndapikey=

# NzbDrone uses SSL (0, 1).
#
# Set to 1 if using SSL, else set to 0.
#ndssl=0

# NzbDrone web root.
#
# set this if using a reverse proxy.
#ndweb_root=

## HeadPhones

# HeadPhones script category.
#
# category that gets called for post-processing with HeadHones.
#hpCategory=music

# HeadPhones api key.
#hpapikey=

# HeadPhones host.
#hphost=localhost

# HeadPhones port.
#hpport=8181

# HeadPhones uses ssl (0, 1).
#
# Set to 1 if using ssl, else set to 0.
#hpssl=0

# HeadPhones web_root
#
# set this if using a reverse proxy.
#hpweb_root=

## Mylar

# Mylar script category.
#
# category that gets called for post-processing with Mylar.
#myCategory=comics

# Mylar host.
#myhost=localhost

# Mylar port.
#myport=8090

# Mylar username.
#myusername=

# Mylar password.
#mypassword=

# Mylar uses ssl (0, 1).
#
# Set to 1 if using ssl, else set to 0.
#myssl=0

# Mylar web_root
#
# set this if using a reverse proxy.
#myweb_root=

## Gamez

# Gamez script category.
#
# category that gets called for post-processing with Gamez.
#gzCategory=games

# Gamez api key.
#gzapikey=

# Gamez host.
#gzhost=localhost

# Gamez port.
#gzport=8085

# Gamez uses ssl (0, 1).
#
# Set to 1 if using ssl, else set to 0.
#gzssl=0

# Gamez web_root
#
# set this if using a reverse proxy.
#gzweb_root=

## Extensions

# Media Extensions
#
# This is a list of media extensions that are used to verify that the download does contain valid media.
#mediaExtensions=.mkv,.avi,.divx,.xvid,.mov,.wmv,.mp4,.mpg,.mpeg,.vob,.iso

## Transcoder

# Transcode (0, 1).
#
# set to 1 to transcode, otherwise set to 0.
#transcode=0

# create a duplicate, or replace the original (0, 1).
#
# set to 1 to cretae a new file or 0 to replace the original
#duplicate=1

# ignore extensions
#
# list of extensions that won't be transcoded.
#ignoreExtensions=.avi,.mkv

# ffmpeg output settings.
#outputVideoExtension=.mp4
#outputVideoCodec=libx264
#outputVideoPreset=medium
#outputVideoFramerate=24
#outputVideoBitrate=800k
#outputAudioCodec=libmp3lame
#outputAudioBitrate=128k
#outputSubtitleCodec=

## WakeOnLan

# use WOL (0, 1).
#
# set to 1 to send WOL broadcast to the mac and test the server (e.g. xbmc) on the host and port specified.
#wolwake=0

# WOL MAC
#
# enter the mac address of the system to be woken.
#wolmac=00:01:2e:2D:64:e1

# Set the Host and Port of a server to verify system has woken.
#wolhost=192.168.1.37
#wolport=80

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################
import os
import sys
import nzbtomedia
from nzbtomedia.autoProcess.autoProcessComics import autoProcessComics
from nzbtomedia.autoProcess.autoProcessGames import autoProcessGames
from nzbtomedia.autoProcess.autoProcessMovie import autoProcessMovie
from nzbtomedia.autoProcess.autoProcessMusic import autoProcessMusic
from nzbtomedia.autoProcess.autoProcessTV import autoProcessTV
from nzbtomedia.nzbToMediaUtil import get_dirnames, cleanup_directories
from nzbtomedia import logger

# post-processing
def process(nzbDir, inputName=None, status=0, clientAgent='manual', download_id=None, inputCategory=None):
    result = 0

    # auto-detect section
    section = nzbtomedia.CFG.findsection(inputCategory)
    if section:
        logger.info("Sending %s to %s for post-processing ..." % (inputName, str(section).upper()))
    else:
        logger.error("We could not find a section with containing a download category labeled %s in your autoProcessMedia.cfg, Exiting!" % inputCategory)

    if nzbtomedia.CFG["CouchPotato"][inputCategory]:
        result = autoProcessMovie().process(nzbDir, inputName, status, clientAgent, download_id, inputCategory)
    elif nzbtomedia.CFG["SickBeard", "NzbDrone"][inputCategory]:
        result = autoProcessTV().processEpisode(nzbDir, inputName, status, clientAgent, inputCategory)
    elif nzbtomedia.CFG["HeadPhones"][inputCategory]:
        result = autoProcessMusic().process(nzbDir, inputName, status, clientAgent, inputCategory)
    elif nzbtomedia.CFG["Mylar"][inputCategory]:
        result = autoProcessComics().processEpisode(nzbDir, inputName, status, clientAgent, inputCategory)
    elif nzbtomedia.CFG["Gamez"][inputCategory]:
        result = autoProcessGames().process(nzbDir, inputName, status, clientAgent, inputCategory)

    if result == 0:
        # Clean up any leftover files
        cleanup_directories(inputCategory, section, result, nzbDir)

    return result

def main(args, section=None):
    # Initialize the config
    nzbtomedia.initialize(section)

    # clientAgent for NZBs
    clientAgent = nzbtomedia.NZB_CLIENTAGENT

    logger.info("#########################################################")
    logger.info("## ..::[%s]::.. ##" % os.path.basename(__file__))
    logger.info("#########################################################")

    # debug command line options
    logger.debug("Options passed into nzbToMedia: %s" % args)

    # Post-Processing Result
    result = 0
    status = 0

    # NZBGet V11+
    # Check if the script is called from nzbget 11.0 or later
    if os.environ.has_key('NZBOP_SCRIPTDIR') and not os.environ['NZBOP_VERSION'][0:5] < '11.0':
        logger.info("Script triggered from NZBGet (11.0 or later).")

        if os.environ['NZBOP_UNPACK'] != 'yes':
            logger.error("Please enable option \"Unpack\" in nzbget configuration file, exiting")
            sys.exit(nzbtomedia.NZBGET_POSTPROCESS_ERROR)

        # Check par status
        if os.environ['NZBPP_PARSTATUS'] == '3':
            logger.warning("Par-check successful, but Par-repair disabled, exiting")
            logger.info("Please check your Par-repair settings for future downloads.")
            sys.exit(nzbtomedia.NZBGET_POSTPROCESS_NONE)

        if os.environ['NZBPP_PARSTATUS'] == '1' or os.environ['NZBPP_PARSTATUS'] == '4':
            logger.warning("Par-repair failed, setting status \"failed\"")
            status = 1

        # Check unpack status
        if os.environ['NZBPP_UNPACKSTATUS'] == '1':
            logger.warning("Unpack failed, setting status \"failed\"")
            status = 1

        if os.environ['NZBPP_UNPACKSTATUS'] == '0' and os.environ['NZBPP_PARSTATUS'] == '0':
            # Unpack was skipped due to nzb-file properties or due to errors during par-check

            if os.environ['NZBPP_HEALTH'] < 1000:
                logger.warning("Download health is compromised and Par-check/repair disabled or no .par2 files found. Setting status \"failed\"")
                logger.info("Please check your Par-check/repair settings for future downloads.")
                status = 1

            else:
                logger.info("Par-check/repair disabled or no .par2 files found, and Unpack not required. Health is ok so handle as though download successful")
                logger.info("Please check your Par-check/repair settings for future downloads.")

        # Check if destination directory exists (important for reprocessing of history items)
        if not os.path.isdir(os.environ['NZBPP_DIRECTORY']):
            logger.error("Nothing to post-process: destination directory %s doesn't exist. Setting status failed" % (os.environ['NZBPP_DIRECTORY']))
            status = 1

        # Check for download_id to pass to CouchPotato
        download_id = ""
        if os.environ.has_key('NZBPR_COUCHPOTATO'):
            download_id = os.environ['NZBPR_COUCHPOTATO']

        # All checks done, now launching the script.
        clientAgent = 'nzbget'
        result = process(os.environ['NZBPP_DIRECTORY'], inputName=os.environ['NZBPP_NZBFILENAME'], status=status, clientAgent=clientAgent, download_id=download_id, inputCategory=os.environ['NZBPP_CATEGORY'])
    # SABnzbd Pre 0.7.17
    elif len(args) == nzbtomedia.SABNZB_NO_OF_ARGUMENTS:
        # SABnzbd argv:
        # 1 The final directory of the job (full path)
        # 2 The original name of the NZB file
        # 3 Clean version of the job name (no path info and ".nzb" removed)
        # 4 Indexer's report number (if supported)
        # 5 User-defined category
        # 6 Group that the NZB was posted in e.g. alt.binaries.x
        # 7 Status of post processing. 0 = OK, 1=failed verification, 2=failed unpack, 3=1+2
        clientAgent = 'sabnzbd'
        logger.info("Script triggered from SABnzbd")
        result = process(args[1], inputName=args[2], status=args[7], inputCategory=args[5], clientAgent=clientAgent, download_id='')
    # SABnzbd 0.7.17+
    elif len(args) >= nzbtomedia.SABNZB_0717_NO_OF_ARGUMENTS:
        # SABnzbd argv:
        # 1 The final directory of the job (full path)
        # 2 The original name of the NZB file
        # 3 Clean version of the job name (no path info and ".nzb" removed)
        # 4 Indexer's report number (if supported)
        # 5 User-defined category
        # 6 Group that the NZB was posted in e.g. alt.binaries.x
        # 7 Status of post processing. 0 = OK, 1=failed verification, 2=failed unpack, 3=1+2
        # 8 Failure URL
        clientAgent = 'sabnzbd'
        logger.info("Script triggered from SABnzbd 0.7.17+")
        result = process(args[1], inputName=args[2], status=args[7], inputCategory=args[5], clientAgent=clientAgent, download_id='')
    else:
        # Perform Manual Run
        logger.warning("Invalid number of arguments received from client, Switching to manual run mode ...")

        # Loop and auto-process
        clientAgent = 'manual'
        for section, subsection in nzbtomedia.SUBSECTIONS.items():
            for category in subsection:
                if nzbtomedia.CFG[section][category].isenabled():
                    dirNames = get_dirnames(section, category)
                    for dirName in dirNames:
                        logger.info("Starting manual run for %s:%s - Folder:%s" % (section, category, dirName))
                        results = process(dirName, os.path.basename(dirName), 0, clientAgent=clientAgent, inputCategory=category)
                        if results != 0:
                            logger.error("A problem was reported when trying to perform a manual run for %s:%s." % (section, category))
                            result = results
                else:
                    logger.debug("nzbToMedia %s:%s is DISABLED" % (section, category))

    if result == 0:
        logger.info("The %s script completed successfully." % args[0])
        if os.environ.has_key('NZBOP_SCRIPTDIR'): # return code for nzbget v11
            sys.exit(nzbtomedia.NZBGET_POSTPROCESS_SUCCESS)
    else:
        logger.error("A problem was reported in the %s script." % args[0])
        if os.environ.has_key('NZBOP_SCRIPTDIR'): # return code for nzbget v11
            sys.exit(nzbtomedia.NZBGET_POSTPROCESS_ERROR)

    sys.exit(result)

if __name__ == '__main__':
    main(sys.argv)