import os
import configparser  # noqa: F401
import yaml  # noqa: F401


class ConfigManager(object):

    """
    already in config (move handling here tho):
    aws_access_key_id, # done
    aws_secret_access_key, # done
    save_images_to_s3_bucket,
    save_images_to_s3_folder,
    team, # done
    metadata # done
    eval_name

    Properties we would like to move to the config file (I think?):
    debug,
    enable_noise,
    seed,
    size,
    depth_masks,
    object_masks,
    history_enabled
    (do we want/need to keep depth and object masks properties?)
    """

    CONFIG_FILE_KEY = 'MCS_CONFIG_FILE_PATH'  # TODO: MCS-410: REPLACE
    DEFAULT_CONFIG_FILE = './mcs_config.yaml'  # TODO: MCS-410: REPLACE
    CONFIG_METADATA_TIER = 'metadata'
    CONFIG_AWS_ACCESS_KEY_ID = 'aws_access_key_id'
    CONFIG_AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'
    CONFIG_TEAM = 'team'
    CONFIG_EVALUATION = 'evaluation'
    CONFIG_EVALUATION_NAME = 'evaluation_name'
    CONFIG_S3_BUCKET = 's3_bucket'
    CONFIG_S3_FOLDER = 's3_folder'

    def __init__(self, config_file_path):
        # self.config_file = os.getenv(self.CONFIG_FILE_KEY,
        #                             self.DEFAULT_CONFIG_FILE)

        # For config file, look for environment variable first,
        # then look for config_path parameter from constructor
        self._config_file = os.getenv('MCS_CONFIG_FILE_PATH', config_file_path)

        if(self._config_file is None):
            self._config_file = './mcs_config.yaml'

        self._config = self.read_config_file()

        """"
        # Environment variable override for metadata property
        metadata_env_var = os.getenv('MCS_METADATA_LEVEL', None)

        if(metadata_env_var is None):
            self._metadata_tier = (
                self._config.get(self.CONFIG_METADATA_TIER, '')
            )
        else:
            self._metadata_tier = metadata_env_var
        """

    def read_config_file(self):
        if os.path.exists(self._config_file):
            with open(self._config_file, 'r') as config_file:
                config = yaml.load(config_file)
                # TODO: MCS-410 - Uncomment
                # if self.__debug_to_terminal:
                print('Read MCS Config File:')
                print(config)
                if 'metadata' not in config:
                    config['metadata'] = ''
                return config
        return {}

    def get_metadata_tier(self):
        # Environment variable override for metadata property
        metadata_env_var = os.getenv('MCS_METADATA_LEVEL', None)

        if(metadata_env_var is None):
            return self._config.get(self.CONFIG_METADATA_TIER, '')

        return metadata_env_var

    def is_evaluation(self):
        return self._config.get(self.CONFIG_EVALUATION, False)

    def check_env_variable_prop(self, env_var_key, key):
        env_var = os.getenv(env_var_key, None)

        if(env_var is None):
            return self._config.get(key, '')

        return env_var

    """
    def check_env_variable_prop(self, key):
        metadata_env_var = os.getenv('MCS_METADATA_LEVEL', None)

        if(metadata_env_var is None):
            self._metadata_tier = (
                self._config.get(self.CONFIG_METADATA_TIER, '')
            )
        else:
            self._metadata_tier = metadata_env_var
    """

    def get_property(self, key):
        return (self._config.get(key, ''))

    def get_aws_access_key_id(self):
        return self._config.get(self.CONFIG_AWS_ACCESS_KEY_ID)

    def get_aws_secret_access_key(self):
        return self._config.get(self.CONFIG_AWS_SECRET_ACCESS_KEY)

    def get_evaluation_name(self):
        return self._config.get(self.CONFIG_EVALUATION_NAME, '')

    def get_s3_bucket(self):
        return self._config.get(self.CONFIG_S3_BUCKET, None)

    def get_s3_folder(self):
        return self._config.get(self.CONFIG_S3_FOLDER, None)

    def get_team(self):
        return self._config.get(self.CONFIG_TEAM, '')

    def get_property_with_suffix(self, key, suffix):
        return (self._config.get(key + suffix, ''))

    def has_property(self, key):
        return key in self._config
