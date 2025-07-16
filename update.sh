#!/usr/bin/env bash

bump_minor_version() {
    local PYPROJECT_FILE="${1:-pyproject.toml}"
    
    # Check if pyproject.toml exists
    if [ ! -f "$PYPROJECT_FILE" ]; then
        echo "Error: $PYPROJECT_FILE not found in current directory" >&2
        return 1
    fi

    # Extract current version using grep and sed
    local current_version=$(grep '^version = ' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/')

    if [ -z "$current_version" ]; then
        echo "Error: Could not find version in $PYPROJECT_FILE" >&2
        return 1
    fi

    echo "Current version: $current_version" >&2

    # Parse version components (assuming semantic versioning: major.minor.patch)
    IFS='.' read -r major minor patch <<< "$current_version"

    # Validate that we have numeric components
    if ! [[ "$major" =~ ^[0-9]+$ ]] || ! [[ "$minor" =~ ^[0-9]+$ ]] || ! [[ "$patch" =~ ^[0-9]+$ ]]; then
        echo "Error: Invalid version format. Expected format: major.minor.patch" >&2
        return 1
    fi

    # Increment minor version
    local new_patch=$((patch + 1))
    local new_version="$major.$minor.$new_patch"

    echo "New version: $new_version" >&2

    # Create backup of original file
    cp "$PYPROJECT_FILE" "$PYPROJECT_FILE.backup"

    # Update the version in pyproject.toml
    sed -i "s/^version = \"$current_version\"/version = \"$new_version\"/" "$PYPROJECT_FILE"

    # Verify the change was made
    local updated_version=$(grep '^version = ' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/')

    if [ "$updated_version" = "$new_version" ]; then
        echo "Successfully updated version from $current_version to $new_version" >&2
        echo "Backup saved as $PYPROJECT_FILE.backup" >&2
        
        # Output the new version to stdout
        echo "$new_version"
        return 0
    else
        echo "Error: Version update failed" >&2
        # Restore backup
        mv "$PYPROJECT_FILE.backup" "$PYPROJECT_FILE"
        return 1
    fi
}


version=$(bump_minor_version)
echo "The new version is: $new_version"
echo "$version" > version.txt
