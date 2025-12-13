"""
Settings file for Semantic Search application.
All configurable patterns and options are defined here.
"""
import os
# Data paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CACHE_FILE = os.path.join(DATA_DIR, 'search_cache.pkl')
LOG_FILE = os.path.join(DATA_DIR, 'embeddings_log.txt')
MODEL_CACHE_DIR = os.path.join(DATA_DIR, 'model')

# Root path to search
SEARCH_ROOT = r"C:\Users\Mitt"

# Absolute paths to exclude completely
EXCLUDED_PATHS = [
    r"C:\Users\Mitt\AppData",
    r"C:\Users\Mitt\ScStore",
    r"C:\Users\Mitt\Searches",
]

# Patterns to exclude (matched against path components)
# If any component of a path matches these patterns, it will be excluded
EXCLUDED_PATTERNS = [
    # Python environments & packages
    'venv',
    '.venv',
    'env',
    '.env',
    '__pycache__',
    'site-packages',
    'dist-packages',
    '.eggs',
    'egg-info',
    
    # JavaScript/Node
    'node_modules',
    '.npm',
    '.yarn',
    'bower_components',
    
    # Version Control
    '.git',
    '.svn',
    '.hg',
    '.bzr',
    
    # IDEs & Editors
    '.idea',
    '.vscode',
    '.vs',
    '.eclipse',
    '.settings',
    
    # Build & Distribution
    'build',
    'dist',
    '__MACOSX',
    '.gradle',
    'target',
    'out',
    'bin',
    'obj',
    
    # Cache & Temp
    '.cache',
    '.tmp',
    'temp',
    'tmp',
    '.pytest_cache',
    '.mypy_cache',
    '.tox',
    
    # System & Hidden
    '$RECYCLE.BIN',
    'System Volume Information',
    'Thumbs.db',
    '.DS_Store',
    'desktop.ini',
]

# File extensions to always exclude
EXCLUDED_EXTENSIONS = [
    '.pyc',
    '.pyo',
    '.pyd',
    '.so',
    '.dll',
    '.o',
    '.obj',
    '.exe',
    '.bin',
    '.class',
    '.jar',
    '.war',
    '.res',
    '.voucher',
    '.dat',
    '.lnk',
    '.azw',
    '.mbpV2',
    '.phl'
]

# Classifier settings
CLASSIFIER_TYPE = 'heuristic'  # Options: 'heuristic', future: 'ml'
RELEVANCE_THRESHOLD = 0.5  # Score threshold for heuristic classifier

# Search settings
SEARCH_TOP_K = 5  # Number of results to return

# Positive signals for heuristic classifier
POSITIVE_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.md', '.rst', '.csv', '.json', '.xml', '.yaml', '.yml',
    '.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.h',
    '.go', '.rs', '.rb', '.php', '.sql', '.sh', '.bat', '.ps1',
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp4', '.mp3',
    '.zip', '.rar', '.7z', '.tar', '.gz',
}

POSITIVE_NAMES = {
    'readme', 'license', 'changelog', 'config', 'settings',
    'todo', 'notes', 'docs', 'documentation', 'guide',
    'main', 'index', 'app', 'application', 'project',
}

POSITIVE_FOLDERS = {
    'documents', 'desktop', 'downloads', 'projects', 'work',
    'pictures', 'photos', 'images', 'videos', 'music',
    'src', 'source', 'lib', 'scripts', 'tools',
}
