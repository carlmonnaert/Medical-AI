#!/usr/bin/env python3
"""
Generate documentation for the hospital simulation project using Sphinx and autodoc.

This script sets up and runs Sphinx to create HTML documentation
for all Python modules in the project. Documentation is saved to the ./docs directory.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_docs():
    """Generate HTML documentation using Sphinx with autodoc."""
    # Get project root (parent of src directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add project root to Python path so 'src' module can be found
    sys.path.insert(0, project_root)
    print(f"Adding {project_root} to Python path")
    
    # Set up paths
    docs_dir = os.path.join(project_root, 'docs')
    sphinx_src_dir = os.path.join(docs_dir, 'source')
    sphinx_build_dir = os.path.join(docs_dir, 'build/html')
    
    # Clean previous build if exists
    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    
    # Create docs directory structure
    ensure_dir(docs_dir)
    ensure_dir(sphinx_src_dir)
    ensure_dir(os.path.join(sphinx_src_dir, '_static'))
    ensure_dir(os.path.join(sphinx_src_dir, '_templates'))
    
    # Create Sphinx configuration file
    with open(os.path.join(sphinx_src_dir, 'conf.py'), 'w') as f:
        f.write('''# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Hospital Simulation'
copyright = '2024, IA Medical Team'
author = 'IA Medical Team'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Add the project root directory to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath('../..'))
# Also add src directory explicitly
sys.path.insert(0, os.path.abspath('../../src'))
''')
    
    # Create main index.rst file
    with open(os.path.join(sphinx_src_dir, 'index.rst'), 'w') as f:
        f.write('''Hospital Simulation Documentation
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   modules

Welcome to the Hospital Simulation documentation. This documentation is 
automatically generated from docstrings in the code.

Project Overview
----------------

This project simulates a hospital with multiple specialties and patients, providing
a real-time web dashboard for monitoring hospital operations. Key features include:

* Realistic time-of-day and seasonal patterns for patient arrivals
* Multiple doctor specialties with appropriate allocation
* Detailed data collection and visualization
* Ability to pause and resume simulations

The simulation uses SimPy for discrete event simulation and Flask for the web dashboard.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
''')
    
    # Create modules.rst
    with open(os.path.join(sphinx_src_dir, 'modules.rst'), 'w') as f:
        f.write('''Modules
=======

.. toctree::
   :maxdepth: 4

   config
   data/index
   ml/index
   simulation/index
   utils/index
   visualization/index
   run_dashboard
   run_ml
   run_simulation
''')
        
        # Create directories for submodules
        module_dirs = ['data', 'ml', 'simulation', 'utils', 'visualization']
        for module_dir in module_dirs:
            ensure_dir(os.path.join(sphinx_src_dir, module_dir))
            
            # Create index.rst for each submodule directory
            module_title = module_dir.capitalize()
            with open(os.path.join(sphinx_src_dir, module_dir, 'index.rst'), 'w') as idx_file:
                idx_file.write(f'''{module_title}
{'=' * len(module_title)}

.. toctree::
   :maxdepth: 2

''')
        
        # Process Python files
        src_dir = os.path.join(project_root, 'src')
        current_script = os.path.basename(__file__)
        
        # Find all Python files excluding this script
        py_files = [p for p in Path(src_dir).glob('**/*.py') 
                   if p.name != current_script]
        
        # Create .rst files for each module
        for py_file in py_files:
            rel_path = os.path.relpath(py_file, project_root)
            module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
            module_name = module_path.split('.')[-1]
            module_parts = module_path.split('.')
            
            # If the module is in a subdirectory
            if len(module_parts) > 2:  # e.g., src.data.db
                package_dir = module_parts[1]  # e.g., 'data'
                
                # Add module to appropriate subdirectory index
                if package_dir in module_dirs:
                    submodule_index_path = os.path.join(sphinx_src_dir, package_dir, 'index.rst')
                    with open(submodule_index_path, 'a') as submodule_index:
                        submodule_index.write(f'   {module_name}\n')
                
                    # Create rst file in the subdirectory
                    with open(os.path.join(sphinx_src_dir, package_dir, f'{module_name}.rst'), 'w') as module_file:
                        module_file.write(f'''{module_name}
{'=' * len(module_name)}

.. automodule:: {module_path}
   :members:
   :undoc-members:
   :show-inheritance:
''')
            # Top-level modules
            else:
                # Add module to main modules.rst if it's not already there
                if module_name not in ['config', 'run_dashboard', 'run_ml', 'run_simulation']:
                    f.write(f'   {module_name}\n')
                
                # Create individual module .rst file
                with open(os.path.join(sphinx_src_dir, f'{module_name}.rst'), 'w') as module_file:
                    module_file.write(f'''{module_name}
{'=' * len(module_name)}

.. automodule:: {module_path}
   :members:
   :undoc-members:
   :show-inheritance:
''')
    
    # Try to install required packages
    try:
        subprocess.run([
            sys.executable, 
            "-m", "pip", "install", 
            "sphinx", "sphinx_rtd_theme", "sphinx-autodoc-typehints"
        ], check=True)
    except subprocess.CalledProcessError:
        print("Could not install required packages. Please run:")
        print("pip install sphinx sphinx_rtd_theme sphinx-autodoc-typehints")
        return
    
    # Build the documentation
    try:
        # Change to docs directory
        os.chdir(docs_dir)
        
        # Run sphinx-build
        subprocess.run([
            sys.executable,
            "-m", "sphinx",
            "-b", "html",
            "source", "build/html"
        ], check=True)
        
        print(f"Documentation successfully generated in {sphinx_build_dir}")
        print(f"Open {os.path.join(sphinx_build_dir, 'index.html')} in your browser to view")
        
    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")

if __name__ == "__main__":
    generate_docs()