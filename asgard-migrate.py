from os import listdir, getenv
import os

from argparse import ArgumentParser
from readline import insert_text

from core.server_file import ServerFile

from asgard_sdk.server.server import AsgardServer
from asgard_sdk.client.client import AsgardClient
from asgard_sdk.models.config import Config
from asgard_sdk.models.local import LocalPath
from asgard_sdk.format.print import *

def usage():
    print("asgard-migrate - A script to help you migrate an existing archive of videos into asgard")
    print("Plex Options")
    print("     -pS [section] : Migrate a plex section into an asgard section")
    print("     -pL : Migrate your entire plex library into asgard")
    print("Local Options: ")
    print("     -w [path] : Walk a directory and insert its content into asgard")
    print("     -f [path] : Insert a single item into asgard")
    print("Modifiers: ")
    print("     --section [name] : Set your asgard section")
    print("     --server [name] : Choose a specific server")
    print("     --direct : Directly connect to resources instead of using the REST-API")
    print("     --username [username] : Force a specific username to be logged in migration")

class Migrate(object):
    def __init__(self, direct=False):
        self.direct = direct

        self.config_path = "{}/.config/asgard".format(getenv("HOME"))

        self.config = None
        self.connection = None
        self.section = None

        self.determine_server()

    def determine_connection(self):
        self.connection = AsgardClient(self.config)
        
        if self.direct is True:
            self.connection = AsgardServer(self.config)
            self.connection.connect()

    def determine_server(self, server_name: str = None):
        if os.path.exists(self.config_path) is False:
            print_info("Config path not found. Creating one...")
            os.mkdir(self.config_path)

        for file_name in os.listdir(self.config_path):
            path = self.config_path + "/" + file_name
            server = ServerFile(path)

            if server_name is None:
                if server.is_home == "True":
                    self.config = server
            elif server_name == server.server_name:
                self.config = server
            
        if self.config is None:
            print_error("Failed to find home server. Use --server to specify one", fatal=True)

    def choose_section(self, section_name: str):
        self.section = self.connection.get_section(section_name)

        if self.section is None:
            print_error("Failed to find section: ", section_name, fatal=True)

    # def migrate_section(self, plex_section_name: str):
    #     plex_section = None
    #     for section in self.plex.sections:
    #         if section.title == plex_section_name:
    #             plex_section = section

    #     if plex_section is None:
    #         print_error("Failed to find plex_section: ", plex_section_name)

    def migrate_single(self, path: str, username: str):
        local_path = LocalPath(path)

        print_info("Migration: ", path)
        print_info("Generating SHA-256 checksum... ")
        local_path.get_sha()

        print_info("Creating Asgard object")
        asgard_object = self.connection.get_obj_from_local(local_path)
        asgard_object.file_location = self.section.section_path + "/" + local_path.file_name
        asgard_object.set_upload_info(username)

        print_info("Registering file in database")
        inserted_object = self.connection.create_file(asgard_object, self.section)

        if inserted_object is None:
            print_error("Cannot register file with type {ft} in section with type {st}".format(ft=asgard_object.file_type, st=self.section.section_type))
            return

        print_success("File Registered")
        print("File Name: ", inserted_object.file_name)
        print("File Size: ", inserted_object.file_size)
        print("SHA-256: ", inserted_object.file_sha)
    
    def migrate_bulk(self, path: str, username: str):
        local_path = LocalPath(path)
        
        if local_path.type == "file":
            print_error("You must pass a directory path to do a bulk migrate", fatal=True)
        
        for file_name in listdir(local_path.path):
            file_name = local_path.path + file_name
            self.migrate_single(file_name)

parser = ArgumentParser()

parser.add_argument("--section", action="store", type=str, required=True)
parser.add_argument("--server", action="store", type=str)
parser.add_argument("--direct", action="store_true", default=False)
parser.add_argument("--username", action="store", type=str)

parser.add_argument("-f", "--file", action="store", type=str)
parser.add_argument("-w", "--walk", action="store", type=str)

if __name__ == "__main__":
    args = parser.parse_args()
    
    migrate = Migrate(args.direct)
    migrate.determine_connection()

    username = "default-user"
    if args.username:
        print_warning("A user is being manually specified: ", args.username)
        print_warning("This will deprecated in a later version when authentication is implemented")
        username = args.username

    if args.server:
        migrate.determine_server(args.server)

    if args.section:
        migrate.choose_section(args.section)

    if args.file:
        migrate.migrate_single(args.file, username)

    if args.walk:
        migrate.migrate_bulk(args.walk, username)
    


