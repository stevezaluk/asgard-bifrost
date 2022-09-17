#!/usr/bin/env python3

import sys, os
from argparse import ArgumentParser

from core.cli import CommandLine

DEFAULT_CONFIG_PATH = "{}/.config/asgard-bifrost/".format(os.getenv("HOME"))

def usage():
    print("asgard-bifrost - A command line tool to interact with an asgard server")
    print("Configuration: ")
    print("     -c, --config PATH : The path to your server files. Default is ", DEFAULT_CONFIG_PATH) # this needs to sorted out before initial commit
    print("     --server [server_name] : Choose a server to connect to. Your home server is used by default")
    print("File Interaction: ")
    # print("     -v, --version : Print the server name and the version number")
    print("     -f, --file QUERY : Query an Asgard server for file information")
    print("     -i, --index : List the file names of all files available")
    print("     -s, --search QUERY : Search the server for a file")
    print("     -r, --register PATH : Register a file on asgard without uploading it")
    print("     -S, --sections : List all sections on asgard")
    # print("     -u, --upload PATH : Upload a file to Asgard")
    print("     -cS, --create-section NAME REMOTE_PATH TYPE : Create a new section in Asgard")
    # print("Analytics: ")
    # print("     -p, --popular : List popular files")
    # print("     -rU, --recently-uploaded : List recently uploaded")
    # print("     -rD, --recently-downloaded : List recently downloaded")
    # print("     -f, --favorite QUERY : Favorite a file")
    # print("     -F, --feature QUERY : Feature a file")
    print("Modifiers: ")
    print("     --section SECTION_NAME : Limit your search to a single search")
    print("     --direct : Directly connect to resources instead of using the REST api")
    print("     --full-models : Use full models instead of just file names for searching and indexing")

parser = ArgumentParser()

parser.add_argument("-c", "--config", action="store", default=DEFAULT_CONFIG_PATH) # better documentation on this
parser.add_argument("--server", action="store")

# parser.add_argument("-v", "--version", action="store_true")
parser.add_argument("-f", "--file", action="store", type=str)
parser.add_argument("-i", "--index", action="store_true")
parser.add_argument("-s", "--search", action="store", type=str)
# parser.add_argument("-u", "--upload", action="store")
parser.add_argument("-r", "--register", action="store", type=str)
parser.add_argument("-S", "--sections", action="store_true")

parser.add_argument("-cS", "--create-section", nargs=3, action="store")

parser.add_argument("--section", action="store", type=str)
parser.add_argument("--direct", action="store_true", default=False)
parser.add_argument("--full-models", action="store_true")
parser.add_argument("--skip-upload", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()

    cli = CommandLine(args.direct)
    cli.determine_connection()

    if args.config:
        cli.determine_server(args.config)

    if args.section:
        cli.choose_section(args.section)

    if args.sections:
        cli.sections()

    if args.file:
        cli.file(args.file)

    if args.index:
        cli.index()

    if args.search:
        cli.search(args.search)

    if args.register:
        cli.register_file(args.register)

    if args.create_section:
        section_name = args[0]
        remote_path = args[1]
        type = args[2]        
        
        cli.create_section(section_name=section_name, remote_path=remote_path, type=type)

