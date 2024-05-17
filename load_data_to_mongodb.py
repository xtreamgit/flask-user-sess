#
# Hector:
# REMEMBER:
# 1. Make sure the Mongodb server is running. Use these commands
# Using brew to start MongoDB
#   brew services start mongodb/brew/mongodb-community
#   brew services list
#
# To manually start MongoDB
#   mongod --config /usr/local/etc/mongod.conf
# 
# 2. THIS LOADER CONNECTS TO THE localhost:27017
#
import json
from pymongo import MongoClient, errors
import os
import sys

def print_in_box(messages, color="\033[34m"):
    bold = "\033[1m"
    reset = "\033[0m"
    box_width = max(len(message) for message in messages) + 4
    print(f"{color}{'*' * box_width}{reset}")
    for message in messages:
        print(f"{color}* {bold}{message}{reset}")
    print(f"{color}{'*' * box_width}{reset}")

def load_questions_to_db():
    # ANSI escape codes for formatting
    bold = "\033[1m"
    reset = "\033[0m"
    green = "\033[32m"
    red = "\033[31m"
    blue = "\033[34m"
    yellow = "\033[33m"

    # Check if data.json exists in the root directory
    if not os.path.exists('data.json'):
        print("The data.json file was not found in the root of the project directory. Make sure the data.json is in the root of the project")
        return

    try:
        # Connect to MongoDB - local connection    
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()  # Forces a call to the server to verify the connection
    except errors.ServerSelectionTimeoutError:
        print(f"{bold}{red}Could not connect to MongoDB.\n{reset}{yellow}Check the MongoDB server status with this command:\n{reset}")
        print (f"{bold}{green}\tbrew services list\n{reset}")
        print(f"{bold}{blue}If the MongoDB is status is none, use the following command to start it:\n{reset}")
        print(f"{bold}{green}\tbrew services start mongodb/brew/mongodb-community\n{reset}")
        sys.exit(1)

    # Create Database
    db = client.examDB
    questions_collection = db.questions

    # Ensure the collection is empty before loading new data
    questions_collection.delete_many({})

    # Load data from JSON file
    with open('data.json', 'r') as file:
        questions_data = json.load(file)

    # Insert data into MongoDB
    questions_collection.insert_many(questions_data)

    success_messages = [
        "Data loaded successfully into MongoDB.",
        f"Database Name: {yellow}{db.name}",
        f"Collection Name: {yellow}{questions_collection.name}"
    ]
    print_in_box(success_messages, color="\033[32m")  # Green box for success messages


if __name__ == "__main__":
    load_questions_to_db()
