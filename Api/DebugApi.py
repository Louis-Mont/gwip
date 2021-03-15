class DebugApi:
    def __init__(self, force_reqs=False, force_yes=False):
        """
        :param force_reqs: Forces the reqs even if they are wrong
        :param force_yes: Forces the yes on the edit popup
        """
        self.force_reqs = force_reqs
        self.force_yes = force_yes
