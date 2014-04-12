import os
import sys
import nzbtomedia
from subprocess import call, Popen
from nzbtomedia.nzbToMediaUtil import create_destination
from nzbtomedia import logger

# which() and os_platform() breaks when running in Transmission (has to do with os.environ)

def os_platform():
    # Author Credit: Matthew Scouten @ http://stackoverflow.com/a/7260315
    true_platform = os.environ['PROCESSOR_ARCHITECTURE']
    try:
            true_platform = os.environ["PROCESSOR_ARCHITEW6432"]
    except KeyError:
            pass
            #true_platform not assigned to if this does not exist
    return true_platform


def extract(filePath, outputDestination):
    # Using Windows
    if os.name == 'nt':
        if os_platform() == 'AMD64':
            platform = 'x64'
        else:
            platform = 'x86'
        if not os.path.dirname(sys.argv[0]):
            chplocation = os.path.normpath(os.path.join(os.getcwd(), 'nzbtomedia/extractor/bin/chp.exe'))
            sevenzipLocation = os.path.normpath(os.path.join(os.getcwd(), 'nzbtomedia/extractor/bin/' + platform + '/7z.exe'))
        else:
            chplocation = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), 'nzbtomedia/extractor/bin/chp.exe'))
            sevenzipLocation = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), 'nzbtomedia/extractor/bin/' + platform + '/7z.exe'))
        if not os.path.exists(sevenzipLocation):
            logger.error("EXTRACTOR: Could not find 7-zip, Exiting")
            return False
        else:
            if not os.path.exists(chplocation):
                cmd_7zip = [sevenzipLocation, "x", "-y"]
            else:
                cmd_7zip = [chplocation, sevenzipLocation, "x", "-y"]
            ext_7zip = [".rar",".zip",".tar.gz","tgz",".tar.bz2",".tbz",".tar.lzma",".tlz",".7z",".xz"]
            EXTRACT_COMMANDS = dict.fromkeys(ext_7zip, cmd_7zip)
    # Using unix
    else:
        required_cmds=["unrar", "unzip", "tar", "unxz", "unlzma", "7zr", "bunzip2"]
        ## Possible future suport:
        # gunzip: gz (cmd will delete original archive)
        ## the following do not extract to dest dir
        # ".xz": ["xz", "-d --keep"],
        # ".lzma": ["xz", "-d --format=lzma --keep"],
        # ".bz2": ["bzip2", "-d --keep"],

        EXTRACT_COMMANDS = {
            ".rar": ["unrar", "x", "-o+", "-y"],
            ".tar": ["tar", "-xf"],
            ".zip": ["unzip"],
            ".tar.gz": ["tar", "-xzf"], ".tgz": ["tar", "-xzf"],
            ".tar.bz2": ["tar", "-xjf"], ".tbz": ["tar", "-xjf"],
            ".tar.lzma": ["tar", "--lzma", "-xf"], ".tlz": ["tar", "--lzma", "-xf"],
            ".tar.xz": ["tar", "--xz", "-xf"], ".txz": ["tar", "--xz", "-xf"],
            ".7z": ["7zr", "x"],
            }
        # Test command exists and if not, remove
        if not os.getenv('TR_TORRENT_DIR'):
            for cmd in required_cmds:
                if call(['which', cmd]): #note, returns 0 if exists, or 1 if doesn't exist.
                    for k, v in EXTRACT_COMMANDS.items():
                        if cmd in v[0]:
                            logger.error("EXTRACTOR: %s not found, disabling support for %s", cmd, k)
                            del EXTRACT_COMMANDS[k]
        else:
            logger.warning("EXTRACTOR: Cannot determine which tool to use when called from Transmission")

        if not EXTRACT_COMMANDS:
            logger.warning("EXTRACTOR: No archive extracting programs found, plugin will be disabled")

    ext = os.path.splitext(filePath)
    cmd = []
    if ext[1] in (".gz", ".bz2", ".lzma"):
    # Check if this is a tar
        if os.path.splitext(ext[0])[1] == ".tar":
            cmd = EXTRACT_COMMANDS[".tar" + ext[1]]
    elif ext[1] in (".1", ".01", ".001") and os.path.splitext(ext[0])[1] in (".rar", ".zip", ".7z"): #support for *.zip.001, *.zip.002 etc.
            cmd = EXTRACT_COMMANDS[os.path.splitext(ext[0])[1]]
    else:
        if ext[1] in EXTRACT_COMMANDS:
            cmd = EXTRACT_COMMANDS[ext[1]]
        else:
            logger.debug("EXTRACTOR: Unknown file type: %s", ext[1])
            return False

    # Create outputDestination folder
    create_destination(outputDestination)

    logger.info("Loading config from %s", nzbtomedia.CONFIG_FILE)

    passwordsfile = nzbtomedia.CFG["passwords"]["PassWordFile"]
    if passwordsfile != "" and os.path.isfile(os.path.normpath(passwordsfile)):
        passwords = [line.strip() for line in open(os.path.normpath(passwordsfile))]
    else:
        passwords = []

    logger.info("Extracting %s to %s", filePath, outputDestination)
    logger.debug("Extracting %s %s %s", cmd, filePath, outputDestination)
    pwd = os.getcwd() # Get our Present Working Directory
    os.chdir(outputDestination) # Not all unpack commands accept full paths, so just extract into this directory
    try: # now works same for nt and *nix
        cmd.append(filePath) # add filePath to final cmd arg.
        cmd2 = cmd
        cmd2.append("-p-") # don't prompt for password.
        p = Popen(cmd2) # should extract files fine.
        res = p.wait()
        if (res >= 0 and os.name == 'nt') or res == 0: # for windows chp returns process id if successful or -1*Error code. Linux returns 0 for successful.
            logger.info("EXTRACTOR: Extraction was successful for %s to %s", filePath, outputDestination)
        elif len(passwords) > 0:
            logger.info("EXTRACTOR: Attempting to extract with passwords")
            pass_success = int(0)
            for password in passwords:
                if password == "": # if edited in windows or otherwise if blank lines.
                    continue
                cmd2 = cmd
                #append password here.
                passcmd = "-p" + password
                cmd2.append(passcmd)
                p = Popen(cmd2) # should extract files fine.
                res = p.wait()
                if (res >= 0 and os.name == 'nt') or res == 0: # for windows chp returns process id if successful or -1*Error code. Linux returns 0 for successful.
                    logger.info("EXTRACTOR: Extraction was successful for %s to %s using password: %s", filePath, outputDestination, password)
                    pass_success = int(1)
                    break
                else:
                    continue
            if pass_success == int(0):
                logger.error("EXTRACTOR: Extraction failed for %s. 7zip result was %s", filePath, res)
    except:
        logger.error("EXTRACTOR: Extraction failed for %s. Could not call command %s", filePath, cmd)
    os.chdir(pwd) # Go back to our Original Working Directory
    return True
