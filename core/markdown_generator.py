import os
import pathlib
from fnmatch import fnmatch

def parse_gitignore(directory):
    """
    Parse the .gitignore file in the directory to get a list of patterns to exclude.

    Args:
        directory (str): Path to the directory containing the .gitignore file.

    Returns:
        list: A list of patterns to exclude based on the .gitignore file.
    """
    gitignore_path = os.path.join(directory, ".gitignore")
    exclude_patterns = []
    # Add standard exclusions
    standard_exclusions = [
        ".git/", ".venv/", ".idea/", ".DS_Store", "Thumbs.db", "node_modules/", "__pycache__",
        "build/", "dist/", ".env/", ".eggs/", "*.egg-info/", "*.log", "generated/", "outputs/", "androidTest/", "test/"
    ]
    exclude_patterns.extend(standard_exclusions)

    if os.path.isfile(gitignore_path):
        print(f"Parsing .gitignore file: {gitignore_path}")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                # Skip comments and empty lines
                line = line.strip()
                if line and not line.startswith("#"):
                    # Remove leading slash from pattern to ensure it matches relative paths correctly
                    if line.startswith("/"):
                        line = line[1:]
                    exclude_patterns.append(line)
    else:
        print("No .gitignore file found.")
    return exclude_patterns


def should_exclude(path, exclude_patterns, root_dir):
    """
    Check if a given path matches any of the exclude patterns.

    Args:
        path (str): The path to check.
        exclude_patterns (list): List of patterns to exclude.
        root_dir (str): Root directory to resolve relative patterns.

    Returns:
        bool: True if the path should be excluded, False otherwise.
    """
    relative_path = os.path.relpath(path, root_dir).replace("\\", "/")  # Normalize to forward slashes
    path_parts = relative_path.split("/")

    for pattern in exclude_patterns:
        if pattern.endswith("/"):
            # This is a directory pattern
            dir_pattern = pattern.rstrip("/")
            # Check if dir_pattern occurs as any directory segment in the path
            if dir_pattern in path_parts:
                return True
        else:
            # For file patterns, just use fnmatch
            if fnmatch(relative_path, pattern):
                return True

    return False

def generate_file_structure(directory, indent="", exclude_patterns=None, root_dir=None, focus_subdir=None):
    """
    Recursively generate the structure of files and folders in markdown format, excluding files and folders based on .gitignore.

    Args:
        directory (str): Path to the directory to scan.
        indent (str): Current indentation for nested structures.
        exclude_patterns (list): List of patterns to exclude.
        root_dir (str): Root directory to resolve relative paths.
        focus_subdir (str): Subdirectory to expand in detail (e.g., "app").

    Returns:
        str: Markdown-formatted string representing the directory structure.
    """
    if exclude_patterns is None:
        exclude_patterns = []
    if root_dir is None:
        root_dir = directory

    abs_focus = os.path.abspath(os.path.join(root_dir, focus_subdir)) if focus_subdir else None
    abs_directory = os.path.abspath(directory)

    # Determine if we're currently inside the focus_subdir tree
    # This is true if:
    #   - focus_subdir is defined
    #   - The current directory (abs_directory) is the focus directory or a subdirectory of it
    inFocus = False
    if focus_subdir and abs_directory.startswith(abs_focus):
        inFocus = True


    structure = ""
    for item in sorted(os.listdir(directory)):
        item_path = os.path.join(directory, item)
        abs_item_path = os.path.abspath(item_path)

        # Check if this item should be excluded by .gitignore patterns
        if should_exclude(item_path, exclude_patterns, root_dir):
            continue
        is_dir = os.path.isdir(item_path)

        if is_dir:
            # If not in focus yet but this directory is exactly the focus_subdir, expand it
            if not inFocus and focus_subdir and abs_item_path == abs_focus:
                structure += f"{indent}- {item}/\n"
                structure += generate_file_structure(item_path, indent + "  ", exclude_patterns, root_dir, focus_subdir)
            # If we're already inside the focus directory, keep expanding
            elif inFocus:
                structure += f"{indent}- {item}/\n"
                structure += generate_file_structure(item_path, indent + "  ", exclude_patterns, root_dir, focus_subdir)
            else:
                # Outside the focus directory tree, just list the directory
                structure += f"{indent}- {item}/\n"
        else:
            # It's a file, just list it
            structure += f"{indent}- {item}\n"

    return structure

def include_readme(directory):
    """
    Include the content of README.md or README.txt if it exists in the directory.

    Args:
        directory (str): Path to the directory to check for README files.

    Returns:
        str: Content of the README file or an empty string if no README is found.
    """
    print(f"Looking for README files in: {directory}")
    for readme_file in ["README.md", "README.txt"]:
        readme_path = os.path.join(directory, readme_file)
        if os.path.isfile(readme_path):
            print(f"Found README file: {readme_path}")
            with open(readme_path, "r", encoding="utf-8") as f:
                # Return the content of the README file
                return f"### Project README\n\n{f.read()}\n\n"
    print("No README file found.")
    return ""


def include_kotlin_files(directory, exclude_patterns=None, root_dir=None):
    """
    Include the content of all Kotlin files in the directory and its subdirectories, excluding files based on .gitignore.

    Args:
        directory (str): Path to the directory to scan for Kotlin files.
        exclude_patterns (list): List of patterns to exclude.
        root_dir (str): Root directory to resolve relative paths.

    Returns:
        str: Markdown-formatted string with the content of Kotlin files.
    """
    if exclude_patterns is None:
        exclude_patterns = []
    if root_dir is None:
        root_dir = directory

    print(f"Including Kotlin files from: {directory}")
    content = ""
    for root, _, files in os.walk(directory):
        if should_exclude(root, exclude_patterns, root_dir):
            print(f"Excluding directory: {root}")
            continue
        print(f"Entering directory: {root}")
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".kt") and not should_exclude(file_path, exclude_patterns, root_dir):
                print(f"Reading Kotlin file: {file_path}")
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    # Read the file content and format it for markdown
                    file_content = f.read()
                relative_path = os.path.relpath(file_path, directory)
                content += f"## File: {relative_path}\n\n```kotlin\n{file_content}\n```\n"
    return content


def include_gradle_and_toml_files(directory):
    """
    Include the content of Gradle (.gradle.kts) and version catalog (libs.versions.toml) files.

    Args:
        directory (str): Path to the directory to scan for Gradle and TOML files.

    Returns:
        str: Markdown-formatted string with the content of these files.
    """
    print(f"Including Gradle and TOML files from: {directory}")
    content = ""
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".gradle.kts") or file == "libs.versions.toml":
                print(f"Reading configuration file: {file_path}")
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_content = f.read()
                relative_path = os.path.relpath(file_path, directory)
                if file.endswith(".gradle.kts"):
                    content += f"### Gradle Script: {relative_path}\n\n```kotlin\n{file_content}\n```\n"
                elif file == "libs.versions.toml":
                    content += f"### Version Catalog: {relative_path}\n\n```toml\n{file_content}\n```\n"
    return content


def generate_markdown(directory, output_file="android_project_overview.md", focus_subdir="app"):
    """
    Generate a markdown file summarizing the project structure and content.

    Args:
        directory (str): Path to the project directory.
        output_file (str): Name of the output markdown file.
        focus_subdir (str): Subdirectory to expand in detail (e.g., "app").
    """
    print(f"Generating markdown for directory: {directory}")
    # Parse .gitignore to get exclude patterns
    exclude_patterns = parse_gitignore(directory)

    markdown_content = "# Android Project Overview\n\n"

    # Add file structure section
    print("Adding file structure to markdown.")
    markdown_content += "## File Structure\n\n"
    markdown_content += "This section provides an organized view of the project's directory and file structure, highlighting authored files.\n\n"
    markdown_content += generate_file_structure(directory, exclude_patterns=exclude_patterns, root_dir=directory, focus_subdir=focus_subdir) + "\n\n"

    # Add README content section
    print("Adding README content to markdown.")
    markdown_content += "## Project Documentation\n\n"
    markdown_content += include_readme(directory)

    # Add Kotlin file contents section
    print("Adding Kotlin file contents to markdown.")
    markdown_content += "## Extracted Kotlin Files\n\n"
    markdown_content += "Below are the contents of Kotlin files in the project, organized by file paths.\n\n"
    markdown_content += include_kotlin_files(directory, exclude_patterns=exclude_patterns, root_dir=directory)

    # Add Gradle and TOML files section
    print("Adding Gradle and TOML file contents to markdown.")
    markdown_content += "## Configuration Files\n\n"
    markdown_content += include_gradle_and_toml_files(directory)

    # Ensure output file is saved in a results directory in the script's directory
    script_dir = pathlib.Path(__file__).parent.resolve()
    results_dir = os.path.join(script_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    output_file_path = os.path.join(results_dir, output_file)

    # Write the markdown content to the output file
    print(f"Writing markdown to output file: {output_file_path}")
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file generated: {output_file_path}")

def generate_markdown_with_excludes(directory, output_file_path, user_excluded_paths):
    """
    Generate a markdown file, but also exclude any paths the user unchecked in the Treeview.

    Args:
        directory (str): Path to the project directory.
        output_file_path (str): Absolute path for the output markdown file.
        user_excluded_paths (list): A list of absolute paths that the user wants excluded.
    """
    # 1. Get base exclude patterns from .gitignore
    exclude_patterns = parse_gitignore(directory)

    # 2. Convert each user-excluded path into a relative pattern and add to exclude_patterns
    for abs_path in user_excluded_paths:
        rel_path = os.path.relpath(abs_path, directory).replace("\\", "/")
        # If it's a directory, we might add a trailing slash
        if os.path.isdir(abs_path):
            rel_path = rel_path.rstrip("/") + "/"
        exclude_patterns.append(rel_path)

    # 3. Now do the same logic as generate_markdown, except using exclude_patterns
    markdown_content = "# Project Overview\n\n"

    # File structure
    markdown_content += "## File Structure\n\n"
    markdown_content += (
        "This section outlines the hierarchical structure of the project's files and directories.\n\n"
    )
    markdown_content += generate_file_structure(
        directory,
        exclude_patterns=exclude_patterns,
        root_dir=directory,
        focus_subdir="app"
    )
    markdown_content += "\n\n"

    # README
    markdown_content += "## Project Documentation\n\n"
    markdown_content += include_readme(directory)

    # Add Kotlin file contents section
    print("Adding Kotlin file contents to markdown.")
    markdown_content += "## Extracted Kotlin Files\n\n"
    markdown_content += "Below are the contents of Kotlin files in the project, organized by file paths.\n\n"
    markdown_content += include_kotlin_files(directory, exclude_patterns=exclude_patterns, root_dir=directory)

    # Add Gradle and TOML files section
    print("Adding Gradle and TOML file contents to markdown.")
    markdown_content += "## Configuration Files\n\n"
    markdown_content += include_gradle_and_toml_files(directory)


    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file_path)
    os.makedirs(output_dir, exist_ok=True)

    # Write to disk
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file generated at: {output_file_path}")