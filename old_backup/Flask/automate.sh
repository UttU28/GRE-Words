#!/bin/bash

# Specify the directory to remove
directory_to_remove="GRE-Words"

# Specify the Git repository URL
repo_url="https://github.com/UttU28/GRE-Words.git"

# Remove the existing directory
echo "Removing existing directory: $directory_to_remove"
rm -rf "$directory_to_remove"

# Clone the Git repository
echo "Cloning repository: $repo_url"
git clone "$repo_url"

# Get the repository name from the URL
repo_name=$(basename "$repo_url" .git)

# Set the current directory to the cloned repository
echo "Setting current directory to: $repo_name"
cd "$repo_name"
cd "Flask"

echo "Automation complete!"
