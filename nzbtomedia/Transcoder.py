import errno
import os
import sys
import nzbtomedia
from subprocess import call
from nzbtomedia import logger

class Transcoder:
    def Transcode_directory(self, dirName):
        if os.name == 'nt':
            ffmpeg = os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg\\bin\\ffmpeg.exe') # note, will need to package in this dir.
            useNiceness = False
            if not os.path.isfile(ffmpeg): # problem
                logger.error("ffmpeg not found. ffmpeg needs to be located at: %s", ffmpeg)
                logger.info("Cannot transcode files in folder %s", dirName)
                return 1 # failure
        else:
            if call(['which', 'ffmpeg']) != 0:
                res = call([os.path.join(os.path.dirname(sys.argv[0]),'getffmpeg.sh')])
                if res or call(['which', 'ffmpeg']) != 0: # did not install or ffmpeg still not found.
                    logger.error("Failed to install ffmpeg. Please install manually")
                    logger.info("Cannot transcode files in folder %s", dirName)
                    return 1 # failure
                else:
                    ffmpeg = 'ffmpeg'
            else:
                ffmpeg = 'ffmpeg'
            useNiceness = True

        logger.info("Loading config from %s", nzbtomedia.CONFIG_FILE)

        if not nzbtomedia.CFG:
            logger.error("You need an autoProcessMedia.cfg file - did you rename and edit the .sample?")
            return 1 # failure

        mediaContainer = (nzbtomedia.CFG["Transcoder"]["duplicate"])
        duplicate = int(nzbtomedia.CFG["Transcoder"]["duplicate"])
        ignoreExtensions = (nzbtomedia.CFG["Transcoder"]["ignoreExtensions"])
        outputVideoExtension = nzbtomedia.CFG["Transcoder"]["outputVideoExtension"].strip()
        outputVideoCodec = nzbtomedia.CFG["Transcoder"]["outputVideoCodec"].strip()
        outputVideoPreset = nzbtomedia.CFG["Transcoder"]["outputVideoPreset"].strip()
        outputVideoFramerate = nzbtomedia.CFG["Transcoder"]["outputVideoFramerate"].strip()
        outputVideoBitrate = nzbtomedia.CFG["Transcoder"]["outputVideoBitrate"].strip()
        outputAudioCodec = nzbtomedia.CFG["Transcoder"]["outputAudioCodec"].strip()
        outputAudioBitrate = nzbtomedia.CFG["Transcoder"]["outputAudioBitrate"].strip()
        outputSubtitleCodec = nzbtomedia.CFG["Transcoder"]["outputSubtitleCodec"].strip()
        outputFastStart = int(nzbtomedia.CFG["Transcoder"]["outputFastStart"])
        outputQualityPercent = int(nzbtomedia.CFG["Transcoder"]["outputQualityPercent"])

        niceness = None
        if useNiceness:niceness = int(nzbtomedia.CFG["Transcoder"]["niceness"])

        map(lambda ext: ext.strip(), mediaContainer)
        map(lambda ext: ext.strip(), ignoreExtensions)

        logger.info("Checking for files to be transcoded")
        final_result = 0 # initialize as successful
        for dirpath, dirnames, filenames in os.walk(dirName):
            for file in filenames:
                filePath = os.path.join(dirpath, file)
                name, ext = os.path.splitext(filePath)
                if ext in mediaContainer:  # If the file is a video file
                    if ext in ignoreExtensions:
                        logger.info("No need to transcode video type %s", ext)
                        continue
                    if ext == outputVideoExtension: # we need to change the name to prevent overwriting itself.
                        outputVideoExtension = '-transcoded' + outputVideoExtension # adds '-transcoded.ext'
                    newfilePath = os.path.normpath(name + outputVideoExtension)

                    command = [ffmpeg, '-loglevel', 'warning', '-i', filePath, '-map', '0'] # -map 0 takes all input streams

                    if useNiceness:
                        command = ['nice', '-%d' % niceness] + command

                    if len(outputVideoCodec) > 0:
                        command.append('-c:v')
                        command.append(outputVideoCodec)
                        if outputVideoCodec == 'libx264' and outputVideoPreset:
                            command.append('-preset')
                            command.append(outputVideoPreset)
                    else:
                        command.append('-c:v')
                        command.append('copy')
                    if len(outputVideoFramerate) > 0:
                        command.append('-r')
                        command.append(str(outputVideoFramerate))
                    if len(outputVideoBitrate) > 0:
                        command.append('-b:v')
                        command.append(str(outputVideoBitrate))
                    if len(outputAudioCodec) > 0:
                        command.append('-c:a')
                        command.append(outputAudioCodec)
                        if outputAudioCodec == 'aac': # Allow users to use the experimental AAC codec that's built into recent versions of ffmpeg
                            command.append('-strict')
                            command.append('-2')
                    else:
                        command.append('-c:a')
                        command.append('copy')
                    if len(outputAudioBitrate) > 0:
                        command.append('-b:a')
                        command.append(str(outputAudioBitrate))
                    if outputFastStart > 0:
                        command.append('-movflags')
                        command.append('+faststart')
                    if outputQualityPercent > 0:
                        command.append('-q:a')
                        command.append(str(outputQualityPercent))
                    if len(outputSubtitleCodec) > 0: # Not every subtitle codec can be used for every video container format!
                        command.append('-c:s')
                        command.append(outputSubtitleCodec) # http://en.wikibooks.org/wiki/FFMPEG_An_Intermediate_Guide/subtitle_options
                    else:
                        command.append('-sn')  # Don't copy the subtitles over
                    command.append(newfilePath)

                    try: # Try to remove the file that we're transcoding to just in case. (ffmpeg will return an error if it already exists for some reason)
                        os.remove(newfilePath)
                    except OSError, e:
                        if e.errno != errno.ENOENT: # Ignore the error if it's just telling us that the file doesn't exist
                            logger.debug("Error when removing transcoding target: %s", e)
                    except Exception, e:
                        logger.debug("Error when removing transcoding target: %s", e)

                    logger.info("Transcoding video: %s", file)
                    cmd = ""
                    for item in command:
                        cmd = cmd + " " + item
                    logger.debug("calling command:%s", cmd)
                    result = 1 # set result to failed in case call fails.
                    try:
                        result = call(command)
                    except:
                        logger.error("Transcoding of video %s has failed", filePath)
                    if result == 0:
                        logger.info("Transcoding of video %s to %s succeeded", filePath, newfilePath)
                        if duplicate == 0: # we get rid of the original file
                            os.unlink(filePath)
                    else:
                        logger.error("Transcoding of video %s to %s failed", filePath, newfilePath)
                    # this will be 0 (successful) it all are successful, else will return a positive integer for failure.
                    final_result = final_result + result
        return final_result
