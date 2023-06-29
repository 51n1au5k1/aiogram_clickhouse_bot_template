# function/bot_helper.py

import os
import configparser

class Helper:
    @staticmethod
    def read_config(config_path):
        """
        This function reads a configuration file and returns a ConfigParser object.
        ConfigParser allows to write Python programs which can be customized by end users easily.

        :param config_path: A string containing the path to the configuration file.
        :return: A ConfigParser object containing the data from the configuration file.
        """
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    @staticmethod
    def create_dir_if_not_exists(dir_path):
        """
        This function creates a directory if it does not already exist.

        :param dir_path: A string containing the path to the directory that should be created.
        :return: None
        """
        # If a path is provided and it does not already exist...
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # If no path is provided, do nothing.
        elif not dir_path:
            pass
