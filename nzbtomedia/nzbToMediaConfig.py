import os
import shutil
import nzbtomedia
import lib.configobj
from itertools import chain

class Sections(dict):
    def isenabled(sections):
        # checks if subsection enabled, returns true/false if subsection specified otherwise returns true/false in {}
        to_return = False
        for section, subsection in sections.items():
            for item in subsection:
                if int(subsection[item]['enabled']) == 1:
                        to_return = True
        return to_return

    @property
    def sections(sections):
        # returns [subsections]
        to_return = []
        for section, subsection in sections.items():
            to_return.append(subsection)
        return list(set(chain.from_iterable(to_return)))

    def __getitem__(self, key):
        # check for key in sections
        if key in self:
            return dict.__getitem__(self, key)

        # check for key in subsections
        to_return = Sections()
        for section, subsection in self.items():
            if key in subsection:
                to_return.update({section:{key:dict.__getitem__(subsection, key)}})
        return to_return

class Section(lib.configobj.Section):
    def isenabled(section):
        # checks if subsection enabled, returns true/false if subsection specified otherwise returns true/false in {}
        if section:
            if int(section['enabled']) == 1:
                    return True
        return False

    def findsection(section, key):
        for subsection in section:
            if key in section[subsection]:
                return subsection

    def __getitem__(self, key):
        # check for key in section
        if key in self.keys():
            return dict.__getitem__(self, key)

        # check for key in subsection
        result = Sections()
        for section in key:
            if section in self:
                subsection = dict.__getitem__(self, section)
                result.update({section: subsection})
        return result

class ConfigObj(lib.configobj.ConfigObj, Section):
    def __init__(self, *args, **kw):
        if len(args) == 0:
            args = (nzbtomedia.CONFIG_FILE,)
        super(lib.configobj.ConfigObj, self).__init__(*args, **kw)
        self.interpolation = False

    @staticmethod
    def migrate():
        global CFG_NEW, CFG_OLD
        CFG_NEW = None
        CFG_OLD = None

        try:
            # check for autoProcessMedia.cfg and create if it does not exist
            if not os.path.isfile(nzbtomedia.CONFIG_FILE):
                shutil.copyfile(nzbtomedia.CONFIG_SPEC_FILE, nzbtomedia.CONFIG_FILE)
            CFG_OLD = config(nzbtomedia.CONFIG_FILE)
        except:
            pass

        try:
            # check for autoProcessMedia.cfg.spec and create if it does not exist
            if not os.path.isfile(nzbtomedia.CONFIG_SPEC_FILE):
                shutil.copyfile(nzbtomedia.CONFIG_FILE, nzbtomedia.CONFIG_SPEC_FILE)
            CFG_NEW = config(nzbtomedia.CONFIG_SPEC_FILE)
        except:
            pass

        # check for autoProcessMedia.cfg and autoProcessMedia.cfg.spec and if they don't exist return and fail
        if not CFG_NEW or not CFG_OLD:
            return False

        subsections = {}
        # gather all new-style and old-style sub-sections
        for newsection, newitems in CFG_NEW.items():
            if CFG_NEW[newsection].sections:
                subsections.update({newsection: CFG_NEW[newsection].sections})
        for section, items in CFG_OLD.items():
            if CFG_OLD[section].sections:
                subsections.update({section: CFG_OLD[section].sections})
            for option, value in CFG_OLD[section].items():
                if option in ["category", "cpsCategory", "sbCategory", "hpCategory", "mlCategory", "gzCategory"]:
                    if not isinstance(value, list):
                        value = [value]

                    # add subsection
                    subsections.update({section: value})
                    CFG_OLD[section].pop(option)
                    continue

        def cleanup_values(values, section):
            for option, value in values.iteritems():
                if section in ['CouchPotato']:
                    if option == ['outputDirectory']:
                        CFG_NEW['Torrent'][option] = os.path.split(os.path.normpath(value))[0]
                        values.pop(option)
                if section in ['CouchPotato', 'HeadPhones', 'Gamez']:
                    if option in ['username', 'password']:
                        values.pop(option)
                if section in ["SickBeard", "NzbDrone"]:
                    if option == "wait_for":  # remove old format
                        values.pop(option)
                    if option == "failed_fork":  # change this old format
                        values['failed'] = 'auto'
                        values.pop(option)
                    if option == "Torrent_ForceLink":
                        values['Torrent_NoLink'] = value
                        values.pop(option)
                    if option == "outputDirectory":  # move this to new location format
                        CFG_NEW['Torrent'][option] = os.path.split(os.path.normpath(value))[0]
                        values.pop(option)
                if section in ["Torrent"]:
                    if option in ["compressedExtensions", "mediaExtensions", "metaExtensions", "minSampleSize"]:
                        CFG_NEW['Extensions'][option] = value
                        values.pop(option)
                    if option == "useLink":  # Sym links supported now as well.
                        if isinstance(value, int):
                            num_value = int(value)
                            if num_value == 1:
                                value = 'hard'
                            else:
                                value = 'no'
            return values

        def process_section(section, subsections=None):
            if subsections:
                for subsection in subsections:
                    if subsection in CFG_OLD.sections:
                        values = CFG_OLD[subsection]
                        if subsection not in CFG_NEW[section].sections:
                            CFG_NEW[section][subsection] = {}
                        for option, value in values.items():
                            CFG_NEW[section][subsection][option] = value
                    elif subsection in CFG_OLD[section].sections:
                        values = CFG_OLD[section][subsection]
                        if subsection not in CFG_NEW[section].sections:
                            CFG_NEW[section][subsection] = {}
                        for option, value in values.items():
                            CFG_NEW[section][subsection][option] = value
            else:
                values = CFG_OLD[section]
                if section not in CFG_NEW.sections:
                    CFG_NEW[section] = {}
                for option, value in values.items():
                    CFG_NEW[section][option] = value

        # convert old-style categories to new-style sub-sections
        for section in CFG_OLD.keys():
            subsection = None
            if section in list(chain.from_iterable(subsections.values())):
                subsection = section
                section = ''.join([k for k,v in subsections.iteritems() if subsection in v])
                process_section(section, subsection)
                #[[v.remove(c) for c in v if c in subsection] for k, v in subsections.items() if k == section]
            elif section in subsections.keys():
                subsection = subsections[section]
                process_section(section, subsection)
                #[[v.remove(c) for c in v if c in subsection] for k,v in subsections.items() if k == section]
            elif section in CFG_OLD.keys():
                process_section(section, subsection)

        # create a backup of our old config
        if os.path.isfile(nzbtomedia.CONFIG_FILE):
            cfgbak_name = nzbtomedia.CONFIG_FILE + ".old"
            if os.path.isfile(cfgbak_name):  # remove older backups
                os.unlink(cfgbak_name)
            os.rename(nzbtomedia.CONFIG_FILE, cfgbak_name)

        # writing our configuration file to 'autoProcessMedia.cfg'
        with open(nzbtomedia.CONFIG_FILE, 'wb') as configFile:
            CFG_NEW.write(configFile)

        return True

    @staticmethod
    def addnzbget():
        CFG_NEW = nzbtomedia.CFG
        section = "CouchPotato"
        envCatKey = 'NZBPO_CPSCATEGORY'
        envKeys = ['ENABLED', 'APIKEY', 'HOST', 'PORT', 'SSL', 'WEB_ROOT', 'DELAY', 'METHOD', 'DELETE_FAILED', 'REMOTECPS', 'WAIT_FOR', 'TIMEPERGIB']
        cfgKeys = ['enabled', 'apikey', 'host', 'port', 'ssl', 'web_root', 'delay', 'method', 'delete_failed', 'remoteCPS', 'wait_for', 'TimePerGiB']
        if os.environ.has_key(envCatKey):
            for index in range(len(envKeys)):
                key = 'NZBPO_CPS' + envKeys[index]
                if os.environ.has_key(key):
                    option = cfgKeys[index]
                    value = os.environ[key]
                    if os.environ[envCatKey] not in CFG_NEW[section].sections:
                        CFG_NEW[section][os.environ[envCatKey]] = {}
                    CFG_NEW[section][os.environ[envCatKey]][option] = value
            CFG_NEW[section][os.environ[envCatKey]]['enabled'] = 1

        section = "SickBeard"
        envCatKey = 'NZBPO_SBCATEGORY'
        envKeys = ['ENABLED', 'HOST', 'PORT', 'USERNAME', 'PASSWORD', 'SSL', 'WEB_ROOT', 'WATCH_DIR', 'FORK', 'DELETE_FAILED', 'DELAY', 'TIMEPERGIB', 'TORRENT_NOLINK', 'NZBEXTRACTIONBY']
        cfgKeys = ['enabled', 'host', 'port', 'username', 'password', 'ssl', 'web_root', 'watch_dir', 'fork', 'delete_failed', 'delay', 'TimePerGiB', 'Torrent_NoLink', 'nzbExtractionBy']
        if os.environ.has_key(envCatKey):
            for index in range(len(envKeys)):
                key = 'NZBPO_SB' + envKeys[index]
                if os.environ.has_key(key):
                    option = cfgKeys[index]
                    value = os.environ[key]
                    if os.environ[envCatKey] not in CFG_NEW[section].sections:
                        CFG_NEW[section][os.environ[envCatKey]] = {}
                    CFG_NEW[section][os.environ[envCatKey]][option] = value
            CFG_NEW[section][os.environ[envCatKey]]['enabled'] = 1

        section = "HeadPhones"
        envCatKey = 'NZBPO_HPCATEGORY'
        envKeys = ['ENABLED', 'APIKEY', 'HOST', 'PORT', 'SSL', 'WEB_ROOT', 'DELAY', 'TIMEPERGIB']
        cfgKeys = ['enabled', 'apikey', 'host', 'port', 'ssl', 'web_root', 'delay', 'TimePerGiB']
        if os.environ.has_key(envCatKey):
            for index in range(len(envKeys)):
                key = 'NZBPO_HP' + envKeys[index]
                if os.environ.has_key(key):
                    option = cfgKeys[index]
                    value = os.environ[key]
                    if os.environ[envCatKey] not in CFG_NEW[section].sections:
                        CFG_NEW[section][os.environ[envCatKey]] = {}
                    CFG_NEW[section][os.environ[envCatKey]][option] = value
            CFG_NEW[section][os.environ[envCatKey]]['enabled'] = 1

        section = "Mylar"
        envCatKey = 'NZBPO_MYCATEGORY'
        envKeys = ['ENABLED', 'HOST', 'PORT', 'USERNAME', 'PASSWORD', 'SSL', 'WEB_ROOT']
        cfgKeys = ['enabled', 'host', 'port', 'username', 'password', 'ssl', 'web_root']
        if os.environ.has_key(envCatKey):
            for index in range(len(envKeys)):
                key = 'NZBPO_MY' + envKeys[index]
                if os.environ.has_key(key):
                    option = cfgKeys[index]
                    value = os.environ[key]
                    if os.environ[envCatKey] not in CFG_NEW[section].sections:
                        CFG_NEW[section][os.environ[envCatKey]] = {}
                    CFG_NEW[section][os.environ[envCatKey]][option] = value
            CFG_NEW[section][os.environ[envCatKey]]['enabled'] = 1

        section = "Gamez"
        envCatKey = 'NZBPO_GZCATEGORY'
        envKeys = ['ENABLED', 'APIKEY', 'HOST', 'PORT', 'SSL', 'WEB_ROOT']
        cfgKeys = ['enabled', 'apikey', 'host', 'port', 'ssl', 'web_root']
        if os.environ.has_key(envCatKey):
            for index in range(len(envKeys)):
                key = 'NZBPO_GZ' + envKeys[index]
                if os.environ.has_key(key):
                    option = cfgKeys[index]
                    value = os.environ[key]
                    if os.environ[envCatKey] not in CFG_NEW[section].sections:
                        CFG_NEW[section][os.environ[envCatKey]] = {}
                    CFG_NEW[section][os.environ[envCatKey]][option] = value
            CFG_NEW[section][os.environ[envCatKey]]['enabled'] = 1

        section = "NzbDrone"
        envCatKey = 'NZBPO_NDCATEGORY'
        envKeys = ['ENABLED', 'HOST', 'PORT', 'USERNAME', 'PASSWORD', 'SSL', 'WEB_ROOT', 'WATCH_DIR', 'FORK', 'DELETE_FAILED', 'DELAY', 'TIMEPERGIB', 'TORRENT_NOLINK', 'NZBEXTRACTIONBY']
        cfgKeys = ['enabled', 'host', 'port', 'username', 'password', 'ssl', 'web_root', 'watch_dir', 'fork', 'delete_failed', 'delay', 'TimePerGiB', 'Torrent_NoLink', 'nzbExtractionBy']
        if os.environ.has_key(envCatKey):
            for index in range(len(envKeys)):
                key = 'NZBPO_ND' + envKeys[index]
                if os.environ.has_key(key):
                    option = cfgKeys[index]
                    value = os.environ[key]
                    if os.environ[envCatKey] not in CFG_NEW[section].sections:
                        CFG_NEW[section][os.environ[envCatKey]] = {}
                    CFG_NEW[section][os.environ[envCatKey]][option] = value
            CFG_NEW[section][os.environ[envCatKey]]['enabled'] = 1

        section = "Extensions"
        envKeys = ['COMPRESSEDEXTENSIONS', 'MEDIAEXTENSIONS', 'METAEXTENSIONS']
        cfgKeys = ['compressedExtensions', 'mediaExtensions', 'metaExtensions']
        for index in range(len(envKeys)):
            key = 'NZBPO_' + envKeys[index]
            if os.environ.has_key(key):
                option = cfgKeys[index]
                value = os.environ[key]
                CFG_NEW[section][option] = value

        section = "Transcoder"
        envKeys = ['TRANSCODE', 'DUPLICATE', 'IGNOREEXTENSIONS', 'OUTPUTVIDEOEXTENSION', 'OUTPUTVIDEOCODEC', 'OUTPUTVIDEOPRESET', 'OUTPUTVIDEOFRAMERATE', 'OUTPUTVIDEOBITRATE', 'OUTPUTAUDIOCODEC', 'OUTPUTAUDIOBITRATE', 'OUTPUTSUBTITLECODEC']
        cfgKeys = ['transcode', 'duplicate', 'ignoreExtensions', 'outputVideoExtension', 'outputVideoCodec', 'outputVideoPreset', 'outputVideoFramerate', 'outputVideoBitrate', 'outputAudioCodec', 'outputAudioBitrate', 'outputSubtitleCodec']
        for index in range(len(envKeys)):
            key = 'NZBPO_' + envKeys[index]
            if os.environ.has_key(key):
                option = cfgKeys[index]
                value = os.environ[key]
                CFG_NEW[section][option] = value

        section = "WakeOnLan"
        envKeys = ['WAKE', 'HOST', 'PORT', 'MAC']
        cfgKeys = ['wake', 'host', 'port', 'mac']
        for index in range(len(envKeys)):
            key = 'NZBPO_WOL' + envKeys[index]
            if os.environ.has_key(key):
                option = cfgKeys[index]
                value = os.environ[key]
                CFG_NEW[section][option] = value

        # create a backup of our old config
        if os.path.isfile(nzbtomedia.CONFIG_FILE):
            cfgbak_name = nzbtomedia.CONFIG_FILE + ".old"
            if os.path.isfile(cfgbak_name):  # remove older backups
                os.unlink(cfgbak_name)
            os.rename(nzbtomedia.CONFIG_FILE, cfgbak_name)

        # writing our configuration file to 'autoProcessMedia.cfg'
        with open(nzbtomedia.CONFIG_FILE, 'wb') as configFile:
            CFG_NEW.write(configFile)

lib.configobj.Section = Section
lib.configobj.ConfigObj = ConfigObj
config = ConfigObj
