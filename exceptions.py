# exceptions.py
class GitError(Exception):
    """Exception raised for Git-related errors"""
    pass

class EnvError(Exception):
    """Exception raised for environment-related errors"""
    pass