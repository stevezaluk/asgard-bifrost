import os

from .server_file import ServerFile

from asgard_sdk.format.print import print_error, print_info, print_success
from asgard_sdk.server.server import AsgardServer
from asgard_sdk.client.client import AsgardClient
from asgard_sdk.models.file import LocalPath

home = os.getenv("HOME")

class CommandLine(object):
    def __init__(self, direct=False):
        self.direct = direct

        self.config_path = "{}/.config/asgard".format(home)

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

    def sections(self):
        if self.section is None:
            sections = self.connection.get_sections()
            print_info("Sections: ")
            for section in sections:
                print("- {n} [{p}] ({s})".format(n=section.section_name, p=section.section_path, s=section.section_size))
            
            print("Counted Items: ", len(sections))
        else:
            print_info("Section: ", self.section.section_name)
            print("Name: ", self.section.section_name)
            print("Path: ", self.section.section_path)
            print("Type: ", self.section.section_type)
            print("Size (bytes): ", self.section.section_size)
            print("Total Downloads: ", self.section.total_downloads)
            print("Total Uploads: ", self.section.total_uploads)
            print("\nMongoDB Collection: ", self.section.mongo_collection)
            print("Plex Section: ", self.section.plex_section)

    def file(self, query: str):
        file = self.connection.get_file(query, self.section)

        if file is None:
            print_error("Failed to find file: ", query, fatal=True)

        file_type = file.file_type

        print_info("General Information")
        print("Name: ", file.file_name)
        print("Location: ", file.file_location)
        print("Size (bytes): ", file.file_size)
        print("Type: ", file.file_type)
        print("SHA-256: ", file.file_sha)

        if file_type == "video":
            print_info("Video Information")
            print("Duration: ", file.duration)
            print("Format: ", file.format)
            print("Resoloution: ", file.resolution)
            print("Video Codec: ", file.video_codec)
            print("Audio Codec: ", file.audio_codec)
            print("Languages: ", file.language)

        if file_type == "document":
            print_info("Document Information")
            print("Title: ", file.title)
            print("Author: ", file.author)
            print("Page Count: ", file.page_count)
            print("Format: ", file.format)

        if file_type == "game":
            print_info("ROM Information")
            print("Console: ", file.console)
            print("Region: ", file.region)
        
        print_info("Upload Information")
        print("Creation Date: ", file.creation_date)
        print("Uploaded Date: ", file.uploaded_date)
        print("Uploaded By: ", file.uploaded_by)
        print("Downloads: ", file.download_count)

    def index(self):
        index = self.connection.index(self.section, key="file_name")

        print_info("Index")
        for file_name in index:
            print(" - ", file_name)

        print("Counted Items: ", len(index))

    def search(self, query: str):
        search = self.connection.search(query, section=self.section, key="file_name")

        print_info("Searching for '{}' in file_name".format(query))
        for file_name in search:
            print(" - ", file_name)

        print("\nCounted Items: ", len(search))

    def register_file(self, path: str):
        if self.section is None:
            print_error("Need a section to register file in!", fatal=True)
        
        local_path = LocalPath(path)
        
        print_info("Register: ", path)
        print_info("Generating SHA-256 check sum...")
        local_path.get_sha()
        local_path.file_location = self.section.section_path + "/" + local_path.file_name
        
        print_info("Creating AsgardObject...")
        asgard_obj = self.connection.get_obj_from_local(local_path)

        print_info("Registering file...")
        file = self.connection.register_file(asgard_obj, self.section)
        if file is None:
            print_error("File type does not match section type", fatal=True)

        print_success("File Registered")
        print("File Name: ", file.file_name)
        print("File Size: ", file.file_size)
        print("SHA-256: ", file.file_sha)

    def create_section(self, section_name: str, remote_path: str, type: str):
        section = self.connection.create_section(section_name, remote_path, type)
        if section is None:
            print_error("Section already exists", fatal=True)

        print_success("Section created: ", section.section_name)
