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

def get_server_file(server_path, server_name=None):
    server_file = None
    
    if os.path.exists(server_path) is False:
        os.mkdir(server_path)

    for file_name in os.listdir(server_path):
        path = server_path + file_name
        server = ServerFile(path)

        if server_name is None:
            if server.is_home == "True":
                server_file = server
                break
        elif server_name == server.server_name:
            server_file = server

    if server_file is None:
        print_error("Failed to find or validate (home) server. Please use --server or change your server file", fatal=True)

    return server_file