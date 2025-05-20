import os
import asyncio
import argparse
from utils import *
from pathlib import Path

# Create argument parser
parser = argparse.ArgumentParser(description="Create file for modules in markdown file")

# Define path argument
parser.add_argument(
    "path",
    nargs="?",
    default=os.getcwd(),
    help="Path to the root folder to scan (default: current directory)",
)

# Parse the argument
args = parser.parse_args()

# Access value
folder_path = Path(args.path)  # Converts to a Path object

# Validate that path exists and is a directory
if not (os.path.exists(folder_path) and os.path.isdir(folder_path)):
    print("Error: No such directory")
    exit(1)


async def main():
    markdown_files = await get_markdown_files(folder_path)
    await get_all_modules_in_files(markdown_files)


asyncio.run(main())
