import os,json
from datetime import datetime 
import re

repo_dir = "sldt-semantic-models"


def extract_model_from_turtle_file(turtle_file_path):
    turtle_file_dir = os.path.dirname(turtle_file_path)
    model = os.path.basename(os.path.dirname(turtle_file_dir)) + "#" + os.path.basename(turtle_file_dir)
    return model
    

def parse_repo_metadata(repo_path):
    directories_without_metadata = []
    metadata_dict = {}

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.ttl'):
                metadata_path = os.path.join(root, 'metadata.json')
                if not os.path.exists(metadata_path):
                    directories_without_metadata.append(root)
                else:
                    with open(metadata_path, 'r') as metadata_file:
                        metadata = json.load(metadata_file)
                        for key, value in metadata.items():
                            if key not in metadata_dict:
                                metadata_dict[key] = {}
                            if value not in metadata_dict[key]:
                                metadata_dict[key][value] = []   
                            metadata_dict[key][value].append(extract_model_from_turtle_file(metadata_path))

    return directories_without_metadata, metadata_dict




def repo_exists():
    return os.path.exists(repo_dir)

def get_last_update_date():
    try:
        if not os.path.exists(repo_dir):
            return None
        last_update_time = os.path.getmtime(repo_dir)
        return datetime.fromtimestamp(last_update_time).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Debug: An error occurred while getting the last update date: {e}")
        return None


def parse_repo_for_missing_files(base_dir):
    without_metadata = []
    without_ttl = []
    no_versions = []

    version_pattern = re.compile(r'^\d+\.\d+\.\d+$')

    def recurse(directory, parent_dir):
        has_ttl = False
        has_metadata = False
        has_version_subdir = False

        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)

            if os.path.isdir(full_path):
                # Check if the directory name is a version pattern
                if version_pattern.match(entry):
                    has_version_subdir = True
                    recurse(full_path, os.path.basename(directory))
                # Check if the directory name starts with "io.catenax"
                elif entry.startswith("io.catenax"):
                    recurse(full_path, entry if not parent_dir else f"{parent_dir}/{entry}")
            elif os.path.isfile(full_path):
                if entry.endswith(".ttl"):
                    has_ttl = True
                elif entry == "metadata.json":
                    has_metadata = True

        # Construct the current directory name with the correct format
        if version_pattern.match(os.path.basename(directory)):
            current_dir_name = f"{parent_dir}:{os.path.basename(directory)}" if parent_dir else os.path.basename(directory)
            if not has_ttl:
                without_ttl.append(current_dir_name)
            if not has_metadata:
                without_metadata.append(current_dir_name)
        elif os.path.basename(directory).startswith("io.catenax") and not has_version_subdir:
            current_dir_name = f"{parent_dir}" if parent_dir else os.path.basename(directory)
            no_versions.append(current_dir_name)

    recurse(base_dir, "")

    return without_metadata, without_ttl, no_versions