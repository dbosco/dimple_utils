#!/bin/bash

# Token Calculator Script
# This script provides a command-line interface for the TokenCalculator utility

set -e  # Exit on any error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIMPLE_UTILS_DIR="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$DIMPLE_UTILS_DIR/examples"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  file <file_path>                    - Calculate tokens for a single file"
    echo "  files <file1> [file2] ...           - Calculate tokens for multiple files"
    echo "  folder <folder_path> [options]      - Calculate tokens for folder contents"
    echo "  folders <folder1> [folder2] ...     - Calculate tokens for multiple folders"
    echo "  pattern <base_path> <pattern>       - Calculate tokens for files matching pattern"
    echo "  patterns <base_path1> <base_path2> <pattern1> <pattern2> - Multiple paths with multiple patterns"
    echo "  language <base_path> <language>     - Calculate tokens for specific language files"
    echo "  languages <base_path1> <base_path2> <lang1> <lang2> - Multiple paths with multiple languages"
    echo "  demo                                - Run demonstration examples"
    echo "  test                                - Run test suite"
    echo ""
    echo "Folder Options:"
    echo "  --recursive                         - Search recursively (default: true)"
    echo "  --no-recursive                      - Don't search recursively"
    echo "  --pattern <pattern>                 - File pattern to match (e.g., '*.py')"
    echo "  --encoding <encoding>               - File encoding (default: utf-8)"
    echo ""
    echo "Examples:"
    echo "  $0 file example.txt"
    echo "  $0 files file1.txt file2.py file3.java"
    echo "  $0 folder src --pattern '*.py'"
    echo "  $0 folders src tests docs --pattern '*.py'"
    echo "  $0 pattern . '*.java'"
    echo "  $0 patterns src tests '*.py' '*.java'"
    echo "  $0 language src python"
    echo "  $0 languages src tests python java"
    echo "  $0 demo"
    echo "  $0 test"
}

# Function to run Python script
run_python() {
    local script_path="$1"
    shift
    python3 "$script_path" "$@"
}

# Function to calculate tokens for a single file
calculate_file_tokens() {
    local file_path="$1"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${RED}Error: File '$file_path' does not exist${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Calculating tokens for file: $file_path${NC}"
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_from_file('$file_path')

print(f\"File: {result['file_path']}\")
print(f\"Tokens: {result['token_count']}\")
print(f\"File size: {result['file_size_bytes']} bytes\")
print(f\"Status: {result['status']}\")
"
}

# Function to calculate tokens for multiple files
calculate_files_tokens() {
    local files=("$@")
    
    echo -e "${BLUE}Calculating tokens for ${#files[@]} files${NC}"
    
    # Create properly formatted Python list
    local file_list="["
    for file in "${files[@]}"; do
        file_list="${file_list}'${file}',"
    done
    file_list="${file_list%,}]"  # Remove trailing comma and close bracket
    
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_from_files($file_list)

print(f\"Total files: {result['total_files']}\")
print(f\"Successful: {result['successful_files']}\")
print(f\"Failed: {result['failed_files']}\")
print(f\"Total tokens: {result['total_tokens']}\")
print(f\"Status: {result['status']}\")
print()
print(\"Individual file results:\")
for file_result in result['file_results']:
    print(f\"  {Path(file_result['file_path']).name}: {file_result['token_count']} tokens\")
"
}

# Function to calculate tokens for folder
calculate_folder_tokens() {
    local folder_path="$1"
    local recursive="true"
    local pattern=""
    local encoding="utf-8"
    
    # Parse additional arguments
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --recursive)
                recursive="true"
                shift
                ;;
            --no-recursive)
                recursive="false"
                shift
                ;;
            --pattern)
                pattern="$2"
                shift 2
                ;;
            --encoding)
                encoding="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done
    
    if [ ! -d "$folder_path" ]; then
        echo -e "${RED}Error: Folder '$folder_path' does not exist${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Calculating tokens for folder: $folder_path${NC}"
    if [ -n "$pattern" ]; then
        echo -e "${YELLOW}Pattern: $pattern${NC}"
    fi
    echo -e "${YELLOW}Recursive: $recursive${NC}"
    
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_from_folder(
    '$folder_path', 
    recursive=$([ "$recursive" = "true" ] && echo "True" || echo "False"),
    file_patterns=['$pattern'] if '$pattern' else None,
    encoding='$encoding'
)

print(f\"Folder: $folder_path\")
print(f\"Total files: {result['total_files']}\")
print(f\"Successful: {result['successful_files']}\")
print(f\"Failed: {result['failed_files']}\")
print(f\"Total tokens: {result['total_tokens']}\")
print(f\"Status: {result['status']}\")
"
}

# Function to calculate tokens by pattern
calculate_pattern_tokens() {
    local base_path="$1"
    local pattern="$2"
    
    if [ ! -d "$base_path" ]; then
        echo -e "${RED}Error: Base path '$base_path' does not exist${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Calculating tokens for pattern '$pattern' in '$base_path'${NC}"
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_by_pattern(['$base_path'], ['$pattern'])

print(f\"Pattern: $pattern\")
print(f\"Total files: {result['total_files']}\")
print(f\"Successful: {result['successful_files']}\")
print(f\"Failed: {result['failed_files']}\")
print(f\"Total tokens: {result['total_tokens']}\")
print(f\"Status: {result['status']}\")
print()
print(\"Pattern-specific results:\")
for pattern_result in result['pattern_results']:
    print(f\"  Pattern '{pattern_result['pattern']}': {pattern_result['file_count']} files\")
"
}

# Function to calculate tokens for multiple folders
calculate_folders_tokens() {
    local folders=()
    local recursive="true"
    local pattern=""
    local encoding="utf-8"
    
    # Parse arguments to separate folders from options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --recursive)
                recursive="true"
                shift
                ;;
            --no-recursive)
                recursive="false"
                shift
                ;;
            --pattern)
                pattern="$2"
                shift 2
                ;;
            --encoding)
                encoding="$2"
                shift 2
                ;;
            -*)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
            *)
                # This is a folder path
                folders+=("$1")
                shift
                ;;
        esac
    done
    
    # Check if we have any folders
    if [ ${#folders[@]} -eq 0 ]; then
        echo -e "${RED}Error: At least one folder path required${NC}"
        usage
        exit 1
    fi
    
    # Validate all folders exist
    for folder in "${folders[@]}"; do
        if [ ! -d "$folder" ]; then
            echo -e "${RED}Error: Folder '$folder' does not exist${NC}"
            exit 1
        fi
    done
    
    echo -e "${BLUE}Calculating tokens for ${#folders[@]} folders${NC}"
    if [ -n "$pattern" ]; then
        echo -e "${YELLOW}Pattern: $pattern${NC}"
    fi
    echo -e "${YELLOW}Recursive: $recursive${NC}"
    
    # Create properly formatted Python list
    local folder_list="["
    for folder in "${folders[@]}"; do
        folder_list="${folder_list}'${folder}',"
    done
    folder_list="${folder_list%,}]"  # Remove trailing comma and close bracket
    
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_from_folders(
    $folder_list,
    recursive=$([ "$recursive" = "true" ] && echo "True" || echo "False"),
    file_patterns=['$pattern'] if '$pattern' else None,
    encoding='$encoding'
)

print(f\"Total folders: {result['total_folders']}\")
print(f\"Total files: {result['total_files']}\")
print(f\"Successful: {result['successful_files']}\")
print(f\"Failed: {result['failed_files']}\")
print(f\"Total tokens: {result['total_tokens']}\")
print(f\"Status: {result['status']}\")
print()
print(\"Folder results:\")
for folder_result in result['folder_results']:
    if folder_result['status'] == 'success':
        print(f\"  {folder_result['folder_path']}: {folder_result['result']['total_files']} files, {folder_result['result']['total_tokens']} tokens\")
    else:
        print(f\"  {folder_result['folder_path']}: ERROR - {folder_result.get('error', 'Unknown error')}\")
"
}

# Function to calculate tokens by multiple patterns
calculate_patterns_tokens() {
    local base_paths=()
    local patterns=()
    local in_patterns=false
    
    # Parse arguments to separate base paths and patterns
    for arg in "$@"; do
        if [[ "$arg" == "--" ]]; then
            in_patterns=true
        elif [ "$in_patterns" = true ]; then
            patterns+=("$arg")
        else
            base_paths+=("$arg")
        fi
    done
    
    # If no -- separator, assume last arguments are patterns
    if [ ${#patterns[@]} -eq 0 ]; then
        # Take last half as patterns
        local total_args=${#base_paths[@]}
        local pattern_start=$((total_args / 2))
        patterns=("${base_paths[@]:$pattern_start}")
        base_paths=("${base_paths[@]:0:$pattern_start}")
    fi
    
    # Validate all base paths exist
    for base_path in "${base_paths[@]}"; do
        if [ ! -d "$base_path" ]; then
            echo -e "${RED}Error: Base path '$base_path' does not exist${NC}"
            exit 1
        fi
    done
    
    echo -e "${BLUE}Calculating tokens for patterns in ${#base_paths[@]} base paths${NC}"
    echo -e "${YELLOW}Base paths: ${base_paths[*]}${NC}"
    echo -e "${YELLOW}Patterns: ${patterns[*]}${NC}"
    
    # Create properly formatted Python lists
    local base_paths_list="["
    for path in "${base_paths[@]}"; do
        base_paths_list="${base_paths_list}'${path}',"
    done
    base_paths_list="${base_paths_list%,}]"
    
    local patterns_list="["
    for pattern in "${patterns[@]}"; do
        patterns_list="${patterns_list}'${pattern}',"
    done
    patterns_list="${patterns_list%,}]"
    
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_by_pattern(
    $base_paths_list,
    $patterns_list,
    recursive=True
)

print(f\"Total patterns: {result['total_patterns']}\")
print(f\"Total files: {result['total_files']}\")
print(f\"Successful: {result['successful_files']}\")
print(f\"Failed: {result['failed_files']}\")
print(f\"Total tokens: {result['total_tokens']}\")
print(f\"Status: {result['status']}\")
print()
print(\"Pattern-specific results:\")
for pattern_result in result['pattern_results']:
    if pattern_result['status'] == 'success':
        print(f\"  Pattern '{pattern_result['pattern']}': {pattern_result['file_count']} files, {pattern_result['result']['total_tokens']} tokens\")
    else:
        print(f\"  Pattern '{pattern_result['pattern']}': {pattern_result['status']}\")
"
}

# Function to calculate tokens by language
calculate_language_tokens() {
    local base_path="$1"
    local language="$2"
    
    if [ ! -d "$base_path" ]; then
        echo -e "${RED}Error: Base path '$base_path' does not exist${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Calculating tokens for '$language' files in '$base_path'${NC}"
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_by_language(['$base_path'], ['$language'])

print(f\"Language: $language\")
print(f\"Total files: {result['total_files']}\")
print(f\"Successful: {result['successful_files']}\")
print(f\"Failed: {result['failed_files']}\")
print(f\"Total tokens: {result['total_tokens']}\")
print(f\"Status: {result['status']}\")
"
}

# Function to calculate tokens by multiple languages
calculate_languages_tokens() {
    local base_paths=()
    local languages=()
    local in_languages=false
    
    # Parse arguments to separate base paths and languages
    for arg in "$@"; do
        if [[ "$arg" == "--" ]]; then
            in_languages=true
        elif [ "$in_languages" = true ]; then
            languages+=("$arg")
        else
            base_paths+=("$arg")
        fi
    done
    
    # If no -- separator, assume last arguments are languages
    if [ ${#languages[@]} -eq 0 ]; then
        # Take last half as languages
        local total_args=${#base_paths[@]}
        local language_start=$((total_args / 2))
        languages=("${base_paths[@]:$language_start}")
        base_paths=("${base_paths[@]:0:$language_start}")
    fi
    
    # Validate all base paths exist
    for base_path in "${base_paths[@]}"; do
        if [ ! -d "$base_path" ]; then
            echo -e "${RED}Error: Base path '$base_path' does not exist${NC}"
            exit 1
        fi
    done
    
    echo -e "${BLUE}Calculating tokens for languages in ${#base_paths[@]} base paths${NC}"
    echo -e "${YELLOW}Base paths: ${base_paths[*]}${NC}"
    echo -e "${YELLOW}Languages: ${languages[*]}${NC}"
    
    # Create properly formatted Python lists
    local base_paths_list="["
    for path in "${base_paths[@]}"; do
        base_paths_list="${base_paths_list}'${path}',"
    done
    base_paths_list="${base_paths_list%,}]"
    
    local languages_list="["
    for lang in "${languages[@]}"; do
        languages_list="${languages_list}'${lang}',"
    done
    languages_list="${languages_list%,}]"
    
    python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$DIMPLE_UTILS_DIR')
from dimple_utils.llm_utils import TokenCalculator

calculator = TokenCalculator()
result = calculator.calculate_tokens_by_language(
    $base_paths_list,
    $languages_list,
    recursive=True
)

print(f\"Total languages: {result['total_languages']}\")
print(f\"Languages: {result['languages']}\")
print(f\"Total files: {result['total_files']}\")
print(f\"Successful: {result['successful_files']}\")
print(f\"Failed: {result['failed_files']}\")
print(f\"Total tokens: {result['total_tokens']}\")
print(f\"Status: {result['status']}\")
print()
print(\"Language-specific results:\")
for lang_result in result['language_results']:
    if lang_result['status'] == 'success':
        print(f\"  {lang_result['pattern']}: {lang_result['file_count']} files, {lang_result['result']['total_tokens']} tokens\")
    else:
        print(f\"  {lang_result['pattern']}: {lang_result['status']}\")
"
}

# Function to run demo
run_demo() {
    echo -e "${GREEN}Running TokenCalculator demonstration...${NC}"
    run_python "$EXAMPLES_DIR/example_token_calculator.py"
}

# Function to run tests
run_tests() {
    echo -e "${GREEN}Running TokenCalculator test suite...${NC}"
    run_python "$DIMPLE_UTILS_DIR/tests/test_token_calculator.py"
}

# Main script logic
main() {
    if [ $# -eq 0 ]; then
        usage
        exit 1
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        file)
            if [ $# -eq 0 ]; then
                echo -e "${RED}Error: File path required${NC}"
                usage
                exit 1
            fi
            calculate_file_tokens "$1"
            ;;
        files)
            if [ $# -eq 0 ]; then
                echo -e "${RED}Error: At least one file path required${NC}"
                usage
                exit 1
            fi
            calculate_files_tokens "$@"
            ;;
        folder)
            if [ $# -eq 0 ]; then
                echo -e "${RED}Error: Folder path required${NC}"
                usage
                exit 1
            fi
            calculate_folder_tokens "$@"
            ;;
        folders)
            if [ $# -eq 0 ]; then
                echo -e "${RED}Error: At least one folder path required${NC}"
                usage
                exit 1
            fi
            calculate_folders_tokens "$@"
            ;;
        pattern)
            if [ $# -lt 2 ]; then
                echo -e "${RED}Error: Base path and pattern required${NC}"
                usage
                exit 1
            fi
            calculate_pattern_tokens "$1" "$2"
            ;;
        patterns)
            if [ $# -lt 3 ]; then
                echo -e "${RED}Error: At least one base path and one pattern required${NC}"
                usage
                exit 1
            fi
            calculate_patterns_tokens "$@"
            ;;
        language)
            if [ $# -lt 2 ]; then
                echo -e "${RED}Error: Base path and language required${NC}"
                usage
                exit 1
            fi
            calculate_language_tokens "$1" "$2"
            ;;
        languages)
            if [ $# -lt 3 ]; then
                echo -e "${RED}Error: At least one base path and one language required${NC}"
                usage
                exit 1
            fi
            calculate_languages_tokens "$@"
            ;;
        demo)
            run_demo
            ;;
        test)
            run_tests
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown command '$command'${NC}"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
