import os

from asgard_sdk.models.config import ClientConfig, Config
from asgard_sdk.format.print import print_error, BLUE, GREEN, NC

class ServerFile(ClientConfig):
    def __init__(self, server_file: str):
        super(ServerFile, self).__init__(server_file)
        
    def __str__(self):
        if self.is_home == "True":
            ret = "{g}{n}{nc}".format(g=GREEN, n=self.server_name, nc=NC)
        else:
            ret = "{b}{n}{nc}".format(b=BLUE, n=self.server_name, nc=NC)
        
        return ret
