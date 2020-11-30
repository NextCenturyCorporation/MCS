import os
import configparser  # noqa: F401
import yaml  # noqa: F401


class ConfigManager(object):

    """
    already in config (move handling here tho):
    aws_access_key_id, # done
    aws_secret_access_key, # done
    debug,
    enable_noise -> noise_enabled
    save_images_to_s3_bucket,
    save_images_to_s3_folder,
    size,
    team, # done
    metadata # done
    eval_name
    seed
    history_enabled

    TODO: MCS-410: update docs about config/what properties exist within it
    """

    CONFIG_FILE_ENV_VAR = 'MCS_CONFIG_FILE_PATH'
    METADATA_ENV_VAR = 'MCS_METADATA_LEVEL'
    DEFAULT_CONFIG_FILE = './mcs_config.ini'

    CONFIG_DEFAULT_SECTION = 'MCS'

    CONFIG_AWS_ACCESS_KEY_ID = 'aws_access_key_id'
    CONFIG_AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'
    CONFIG_DEBUG = 'debug'
    CONFIG_DEBUG_OUTPUT = 'debug_output'
    CONFIG_EVALUATION = 'evaluation'
    CONFIG_EVALUATION_NAME = 'evaluation_name'
    CONFIG_HISTORY_ENABLED = 'history_enabled'
    CONFIG_METADATA_TIER = 'metadata'
    CONFIG_NOISE_ENABLED = 'noise_enabled'
    CONFIG_S3_BUCKET = 's3_bucket'
    CONFIG_S3_FOLDER = 's3_folder'
    CONFIG_SEED = 'seed'
    CONFIG_SIZE = 'size'
    CONFIG_TEAM = 'team'

    # Please keep the aspect ratio as 3:2 because the IntPhys scenes are built
    # on this assumption.
    SCREEN_WIDTH_DEFAULT = 600
    SCREEN_WIDTH_MIN = 450

    def __init__(self, config_file_path=None):
        # For config file, look for environment variable first,
        # then look for config_path parameter from constructor
        self._config_file = os.getenv(
            self.CONFIG_FILE_ENV_VAR, config_file_path)

        if(self._config_file is None):
            self._config_file = self.DEFAULT_CONFIG_FILE

        self._read_config_file()

        self._validate_screen_size()

    def _read_config_file(self):
        self._config = configparser.ConfigParser()
        if os.path.exists(self._config_file):
            self._config.read(self._config_file)

            debug_to_terminal = (
                self.is_debug() or self.get_debug_output() == 'terminal'
            )

            if debug_to_terminal is True:
                print('MCS Config File Path: ' + self._config_file)
                print('Read MCS Config File:')
                print({section: dict(self._config[section])
                       for section in self._config.sections()})

    def _validate_screen_size(self):
        if(self.get_size() < self.SCREEN_WIDTH_MIN):
            self._config.set(
                self.CONFIG_DEFAULT_SECTION,
                self.CONFIG_SIZE,
                str(self.SCREEN_WIDTH_DEFAULT)
            )

    def get_aws_access_key_id(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_AWS_ACCESS_KEY_ID,
            fallback=None
        )

    def get_aws_secret_access_key(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_AWS_SECRET_ACCESS_KEY,
            fallback=None
        )

    def get_debug_output(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_DEBUG_OUTPUT,
            fallback=None
        )

    def get_evaluation_name(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_EVALUATION_NAME,
            fallback=''
        )

    def get_metadata_tier(self):
        # Environment variable override for metadata property
        metadata_env_var = os.getenv('MCS_METADATA_LEVEL', None)

        if(metadata_env_var is None):
            return self._config.get(
                self.CONFIG_DEFAULT_SECTION,
                self.CONFIG_METADATA_TIER,
                fallback=''
            )

        return metadata_env_var

    def get_s3_bucket(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_S3_BUCKET,
            fallback=None
        )

    def get_s3_folder(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_S3_FOLDER,
            fallback=None
        )

    def get_seed(self):
        return self._config.getint(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_SEED,
            fallback=None
        )

    def get_size(self):
        return self._config.getint(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_SIZE,
            fallback=self.SCREEN_WIDTH_DEFAULT
        )

    def get_team(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_TEAM,
            fallback=''
        )

    def is_debug(self):
        # Environment variable override for debug mode
        debug_env_var = os.getenv('MCS_DEBUG_MODE', None)

        if(debug_env_var is None):
            return self._config.getboolean(
                self.CONFIG_DEFAULT_SECTION,
                self.CONFIG_DEBUG,
                fallback=False
            )

        if(debug_env_var is None or
                debug_env_var.lower() == 'false' or
                debug_env_var == '0' or debug_env_var == ''):
            return False
        else:
            return True

    def is_evaluation(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_EVALUATION,
            fallback=False
        )

    def is_history_enabled(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_HISTORY_ENABLED,
            fallback=True
        )

    def is_noise_enabled(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_NOISE_ENABLED,
            fallback=False
        )
