from gw_logging import Log


class Core:
    def __init__(self, log_interface):
        """
        :type log_interface: Log
        """
        self.i_log = log_interface
