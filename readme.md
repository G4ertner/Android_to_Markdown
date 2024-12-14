# Android Project Markdown Generator

This script is designed to help Android developers generate a comprehensive Markdown file summarizing their project. The Markdown file provides an overview of the project's structure, configuration files, and source code, making it easier to share the project's context with tools like ChatGPT.

## Key Features

1. **File Structure Overview**: The script recursively scans the project directory and generates a hierarchical view of files and folders.
   - The `app` folder is expanded fully, showing its entire structure.
   - Other top-level folders are displayed in a collapsed view.
2. **Kotlin File Content Extraction**: The script identifies and includes the content of all `.kt` files authored by the developer.
3. **Configuration Files Inclusion**:
   - Extracts and formats `.gradle.kts` files and `libs.versions.toml`.
   - These files are grouped under a "Configuration Files" section.
4. **README Integration**: Automatically incorporates the content of `README.md` or `README.txt` files from the project directory.

## How It Works

The script performs the following steps:

1. **File Filtering**:
   - Ignores auto-generated files, test directories (`androidTest`, `test`), and other non-essential folders using `.gitignore` or standard exclusion rules.
2. **Focus on ****`app`**** Folder**:
   - Fully expands the `app` folder, listing all its subdirectories and files.
3. **Markdown Output**:
   - Generates a Markdown file with sections for the file structure, project documentation, Kotlin source code, and configuration files.

## Usage

### Prerequisites

- Python 3.6 or higher.
- A basic understanding of Markdown and Android project structures.

### Steps

1. Clone or download this script.

2. Open a terminal or command prompt.

3. Run the script:

   ```bash
   python android_markdown_generator.py
   ```

4. Provide the path to your Android project when prompted.

5. Specify the output Markdown file name (default: `android_project_overview.md`).

6. The Markdown file will be saved in a `results` directory created in the same folder as the script.

### Example

#### Input

- Project directory: `/path/to/android/project`
- Output file: `android_overview.md`

#### Output Markdown

````markdown
# Android Project Overview

## File Structure

This section provides an organized view of the project's directory and file structure, highlighting authored files.

- .gitignore
- app/
  - build.gradle.kts
  - proguard-rules.pro
  - src/
    - main/
      - kotlin/
        - com/example/MyClass.kt
- build.gradle.kts
- settings.gradle.kts

## Project Documentation

### README.md

Your project documentation here.

## Extracted Kotlin Files

### File: app/src/main/kotlin/com/example/MyClass.kt

```kotlin
class MyClass {
    fun example() {
        println("Hello, Android!")
    }
}
````

## Configuration Files

### Gradle Script: build.gradle.kts

```kotlin
plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    compileSdk = 33
    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 33
    }
}
```

```

## Contributing

Feel free to fork the repository, submit pull requests, or open issues for feature requests or bug fixes.

## License

This project is licensed under the MIT License.

```
