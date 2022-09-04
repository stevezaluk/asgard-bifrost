import sys, os
from argparse import ArgumentParser

from asgard_sdk.format.print import print_error, print_info, print_success
from asgard_sdk.server.server import AsgardServer
from asgard_sdk.client.client import AsgardClient
from asgard_sdk.models.file import LocalPath

from config.server_file import get_server_file

# from tabulate import tabulate

DEFAULT_CONFIG_PATH = "{}/.config/asgard-bifrost/".format(os.getenv("HOME"))

def usage():
    print("asgard-bifrost - A command line tool to interact with an asgard server")
    print("Configuration: ")
    print("     -c, --config PATH : The path to your server files. Default is ", DEFAULT_CONFIG_PATH) # this needs to sorted out before initial commit
    print("     --server [server_name] : Choose a server to connect to. Your home server is used by default")
    print("Interaction: ")
    # print("     -v, --version : Print the server name and the version number")
    print("     -f, --file QUERY : Query an Asgard server for file information")
    print("     -i, --index : List the file names of all files available")
    print("     -s, --search QUERY : Search the server for a file")
    print("     -r, --register PATH : Register a file on asgard without uploading it")
    print("     -S, --sections : List all sections on asgard")
    # print("     -u, --upload PATH : Upload a file to Asgard")
    print("     -cS, --create-section NAME REMOTE_PATH TYPE : Create a new section in Asgard")
    print("Modifiers: ")
    print("     --section SECTION_NAME : Limit your search to a single search")
    print("     --direct : Directly connect to resources instead of using the REST api")
    print("     --full-models : Use full models instead of just file names for searching and indexing")

parser = ArgumentParser()

parser.add_argument("-c", "--config", action="store", default=DEFAULT_CONFIG_PATH)
parser.add_argument("--server", action="store")

# parser.add_argument("-v", "--version", action="store_true")
parser.add_argument("-f", "--file", action="store", type=str)
parser.add_argument("-i", "--index", action="store_true")
parser.add_argument("-s", "--search", action="store")
parser.add_argument("-u", "--upload", action="store")
parser.add_argument("-r", "--register", action="store")
parser.add_argument("-S", "--sections", action="store_true")

parser.add_argument("-cS", "--create-section", nargs=3, action="store")

parser.add_argument("--section", action="store", type=str)
parser.add_argument("--direct", action="store_true")
parser.add_argument("--full-models", action="store_true")
parser.add_argument("--skip-upload", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()

    config = get_server_file(args.config, args.server) # TODO: sort this out

    if args.server and len(sys.argv) == 1:
        print("+ Server")
        print("Name: ", config)
        print("Is Home Server? ", config.is_home)

        print("Rest API URL: http://{ip}:{p}/api/v1".format(ip=config.rest_ip, p=config.rest_port))
        
        print("Plex IP: {ip}:{p}".format(ip=config.plex_ip, p=config.plex_port))
        print("Plex Token: ", config.plex_token)

        print("MongoDB IP: {ip}:{p}".format(ip=config.mongo_ip, p=config.mongo_port))

    conn = AsgardClient(config)
    
    if args.direct:
        conn = AsgardServer(config)
        conn.connect()

    print_info("Accessing server: {}".format(config))

    section = None
    if args.section:
        section = conn.get_section(args.section)
        
        if section is None:
            print_error("Failed to find section: ", args.section, fatal=True)

        print_info("Fetching within Section: ", section.section_name)

    if args.file:
        file = conn.get_file(args.file, section)

        if file is None:
            print_error("Failed to find file: ", args.file, fatal=True)

        file_type = file.file_type

        print("\n+ General Information")
        print("Name: ", file.file_name)
        print("Location: ", file.file_location)
        print("Size (bytes): ", file.file_size)
        print("Type: ", file.file_type)
        print("SHA-256: ", file.file_sha)

        if file_type == "video":
            print("\n+ Video Information")
            print("Duration: ", file.duration)
            print("Format: ", file.format)
            print("Resoloution: ", file.resolution)
            print("Video Codec: ", file.video_codec)
            print("Audio Codec: ", file.audio_codec)
            print("Languages: ", file.language)

        if file_type == "document":
            print("\n+ Document Information")
            print("Title: ", file.title)
            print("Author: ", file.author)
            print("Page Count: ", file.page_count)
            print("Format: ", file.format)
        
        print("\n+ Upload Information")
        print("Creation Date: ", file.creation_date)
        print("Uploaded Date: ", file.uploaded_date)
        print("Uploaded By: ", file.uploaded_by)
        print("Downloads: ", file.download_count)

    if args.index:
        index = conn.index(section, key="file_name")

        print("\n+ Index")
        for file_name in index:
            print("- ", file_name)

        print("\nCounted {} items".format(len(index)))

    if args.search:
        search = conn.search(args.search, section=section, key="file_name")

        print("\n+ Searching for '{}' ".format(args.search))
        for file_name in search:
            print("- ", file_name)

        print("\nCounted {} items".format(len(search)))

    if args.sections:
        if section is None:
            sections = conn.get_sections()
            print_info("Sections")
            for section in sections:
                print("- {n} [{p}] ({s})".format(n=section.section_name, p=section.section_path, s=section.section_size))
        else:
            print_info("Section: ", section.section_name)
            print("Name: ", section.section_name)
            print("Path: ", section.section_path)
            print("Type: ", section.section_type)
            print("Size (bytes): ", section.section_size)
            print("Total Downloads: ", section.total_downloads)
            print("Total Uploads: ", section.total_uploads)
            print("\nMongoDB Collection: ", section.mongo_collection)
            print("Plex Section: ", section.plex_section)

    if args.register:
        pass
    
    if args.create_section:
        args = args.create_section

        section_name = args[0]
        remote_path = args[1]
        type = args[2]
        
        section = conn.create_section(section_name, remote_path, type)
        if section is None:
            print_error("Section already exists!", fatal=True)

        print_success("Section Created: ", section.section_name)