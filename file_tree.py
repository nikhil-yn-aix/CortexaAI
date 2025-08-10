
import os
import sys
from pathlib import Path

def should_ignore(path_name):
    """Check if a directory or file should be ignored."""
    ignore_patterns = {
        '__pycache__',
        '.git',
        '.gitignore',
        '.DS_Store',
        'node_modules',
        '.vscode',
        '.idea',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        '.coverage',
        'venv',
        'env',
        '.env',
        'emolearn-app-main',
        '.svg',
        'partial_movie_files',
        'images',
        'texts'
    }
    
    return path_name in ignore_patterns or path_name.startswith('.')

def print_tree(directory, prefix="", is_last=True, show_hidden=False):
    """
    Recursively print directory tree structure.
    
    Args:
        directory: Path to directory
        prefix: String prefix for tree formatting
        is_last: Boolean indicating if this is the last item in current level
        show_hidden: Boolean to show hidden files/directories
    """
    try:
        directory = Path(directory)
        
        if not directory.exists():
            print(f"Error: Directory '{directory}' does not exist")
            return
            
        if not directory.is_dir():
            print(f"Error: '{directory}' is not a directory")
            return
        
        
        try:
            items = list(directory.iterdir())
        except PermissionError:
            print(f"{prefix}├── [Permission Denied]")
            return
            
        
        if not show_hidden:
            items = [item for item in items if not should_ignore(item.name)]
        
        
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            
            
            if is_last_item:
                current_prefix = prefix + "└── "
                next_prefix = prefix + "    "
            else:
                current_prefix = prefix + "├── "
                next_prefix = prefix + "│   "
            
            
            if item.is_dir():
                print(f"{current_prefix}{item.name}/")
                
                print_tree(item, next_prefix, is_last_item, show_hidden)
            else:
                
                try:
                    size = item.stat().st_size
                    if size < 1024:
                        size_str = f" ({size}B)"
                    elif size < 1024 * 1024:
                        size_str = f" ({size/1024:.1f}KB)"
                    else:
                        size_str = f" ({size/(1024*1024):.1f}MB)"
                except:
                    size_str = ""
                
                print(f"{current_prefix}{item.name}{size_str}")
                
    except Exception as e:
        print(f"Error processing directory: {e}")

def main():
    """Main function to handle command line arguments and run the tree printer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Print directory tree structure')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory to analyze (default: current directory)')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Show hidden files and directories')
    parser.add_argument('-s', '--size', action='store_true',
                       help='Show file sizes (default: enabled)')
    
    args = parser.parse_args()
    
    target_dir = Path(args.directory).resolve()
    
    print(f"\nDirectory tree for: {target_dir}")
    print("=" * 50)
    print(f"{target_dir}/")
    
    print_tree(target_dir, show_hidden=args.all)
    print()

if __name__ == "__main__":
    main()