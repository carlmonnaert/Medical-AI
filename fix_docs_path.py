#!/usr/bin/env python3
"""
Fix paths for Sphinx documentation generation.

This script adds the necessary path adjustments and then calls
the main documentation generation script.
"""

import os
import sys
import subprocess

def main():
    """Add project root to Python path and run the documentation generator."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Add project root to Python path so modules can be imported
    sys.path.insert(0, project_root)
    os.environ['PYTHONPATH'] = project_root + os.pathsep + os.environ.get('PYTHONPATH', '')
    
    print(f"Setting PYTHONPATH to include {project_root}")
    
    # Run the documentation generator
    docs_script = os.path.join(project_root, 'src', 'generate_docs.py')
    result = subprocess.run([sys.executable, docs_script], env=os.environ)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())