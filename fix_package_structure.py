#!/usr/bin/env python3
"""
Helper module to create __init__.py files and fix import structure.

This script creates __init__.py files in all directories to ensure
proper package imports and helps fix import issues.
"""

import os
import sys
from pathlib import Path

def create_init_files():
    """Create __init__.py files in all subdirectories of src."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, 'src')
    
    # Find all directories in src
    dirs = [d for d in Path(src_dir).glob('**') if d.is_dir()]
    
    # Add the src directory itself
    dirs.append(Path(src_dir))
    
    # Create __init__.py in each directory
    for d in dirs:
        init_file = d / '__init__.py'
        if not init_file.exists():
            print(f"Creating {init_file}")
            with open(init_file, 'w') as f:
                f.write('"""')
                f.write(f'{d.name.capitalize()} module.\n')
                f.write('"""\n')
    
    print(f"Created __init__.py files in {len(dirs)} directories")

def check_imports():
    """Check if imports are working properly."""
    try:
        # Add project root to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        # Try importing modules
        import src
        import src.config
        
        print("✅ Imports are working correctly")
        print(f"src module found at: {src.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure PYTHONPATH includes the project root directory")
        print(f"Current path: {sys.path}")
        return False

def fix_imports():
    """Add project directory to PYTHONPATH."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Add to .env file for VSCode
    env_file = os.path.join(project_root, '.env')
    
    # Check if PYTHONPATH already exists in .env
    pythonpath_exists = False
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            pythonpath_exists = 'PYTHONPATH=' in content
    
    # Create or update .env file
    if not pythonpath_exists:
        with open(env_file, 'a') as f:
            f.write(f"\nPYTHONPATH={project_root}\n")
        print(f"Added PYTHONPATH={project_root} to .env file")
    else:
        print(".env file already contains PYTHONPATH")
    
    print("\nTo use in your terminal, run:")
    print(f"export PYTHONPATH={project_root}:$PYTHONPATH")
    
    return True

def main():
    """Main entry point."""
    print("Fixing package structure...\n")
    
    # Create __init__.py files
    create_init_files()
    
    print("\nChecking imports...")
    imports_ok = check_imports()
    
    if not imports_ok:
        print("\nTrying to fix imports...")
        fix_imports()
    
    print("\nDone! Your package structure should now be ready to use.")
    print("For documentation, run: ./generate_docs.sh")

if __name__ == "__main__":
    main()