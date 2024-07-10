import os
import subprocess
import sys
import csv
import shutil
import git
from git import Repo
import os
import pandas as pd
import yaml
import json

import pydriller as pydrill
from pydriller import Repository
import subprocess
from pathlib import Path

output_results= 'salt_results.csv'
wworking_link = ''
working_id = ''
failed_path = 'failed_clones_ansible'

 # Look for common SaltStack files and directories
saltstack_files = ['top.sls', 'minion', 'minion.d']
saltstack_dirs = ['salt', 'pillar']
found_files = []
found_dirs = []


def clone_repo(): 
    global working_link
    repo_dir = working_link.replace('/', '_')
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)
    else:
        print(f"Directory already exists: {repo_dir}")
        return None
    try:
        repo = Repo.clone_from(working_link, repo_dir)
        print("Cloned!")
        return repo_dir
    except Exception as e:
        return None

def delete_dir():
    if os.path.exists('venv/output_file'):
        shutil.rmtree('venv/output_file')
        print(f"Directory {'venv/output_file'} has been removed.")
    else:
        print(f"Directory {'venv/output_file'} does not exist.")

def delete_cloned_repo(repo_path):
    if os.path.exists(repo_path):
        try:
            # Empty the directory first
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                    except FileNotFoundError as e:
                        print(f"File not found: {e}")
                for dir in dirs:
                    try:
                        dir_path = os.path.join(root, dir)
                        shutil.rmtree(dir_path)
                    except FileNotFoundError as e:
                        print(f"Directory not found: {e}")
            # Delete the now-empty directory
            shutil.rmtree(repo_path)
            print(f"Repository at {repo_path} has been deleted.")
        except Exception as e:
            print(f"An error occurred while deleting the repository at {repo_path}: {e}")
    else:
        print(f"Repository at {repo_path} does not exist.")

def run_salt_lint(directory):
    try:
        result = subprocess.run(['salt-lint', directory], capture_output=True, text=True)
        if result.returncode == 0:
            print("No SaltStack linting issues found.")
            return 1
        else:
            print("SaltStack linting issues found:")
            print(result.stdout)
            return 1
    except FileNotFoundError:
        print("salt-lint is not installed. Please install it using 'pip install salt-lint'.")
        sys.exit(1)

def write_csv_header():
        with open(output_results, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['link', 'id', 'Saltstack'])  # Write header

def write_csv_file(id, link, result):
    with open(output_results, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([link, id, result])

def copy_pair(link, id):
    global working_id
    global working_link
    working_link = link
    working_id = id
    print(working_link)
    print(working_id)

def populate_found_elements(repo_dir):
    global found_dirs
    global found_files
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file in saltstack_files or file.endswith('.sls'):
                found_files.append(os.path.join(root, file))
        for dir in dirs:
            if dir in saltstack_dirs:
                found_dirs.append(os.path.join(root, dir))

def salt_main(repo_dir):
    flag = run_salt_lint(repo_dir)
    populate_found_elements(repo_dir)

    if found_files or found_dirs:
        print("Found SaltStack files or directories:")
        flag = run_salt_lint(repo_dir)
    else:
        print("No SaltStack files or directories found.")
        flag = 0
    
    return flag