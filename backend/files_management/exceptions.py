"""
Domain exceptions for files_management.

Services should raise these exceptions when a file operation fails for a
known business reason. API views can then translate them into stable
client responses.
"""


class FileManagementError(Exception):
    """
    Base exception for all files_management domain errors.
    """


class FileValidationError(FileManagementError):
    """
    Raised when an uploaded file violates validation rules.
    """


class FileAccessDenied(FileManagementError):
    """
    Raised when an actor is not allowed to perform a file action.
    """


class FileNotAvailable(FileManagementError):
    """
    Raised when a file cannot be used because of its lifecycle status.
    """


class FileAttachmentError(FileManagementError):
    """
    Raised when attaching or detaching a file fails.
    """


class FileVersionError(FileManagementError):
    """
    Raised when a file version operation is invalid.
    """


class FileDeletionError(FileManagementError):
    """
    Raised when deletion cannot be requested or completed safely.
    """


class ExternalFileLinkError(FileManagementError):
    """
    Raised when an external file link is invalid or unsupported.
    """


class SignedUrlGenerationError(FileManagementError):
    """
    Raised when a signed URL cannot be generated.
    """