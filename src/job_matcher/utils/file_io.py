from job_matcher.core.exceptions import FileTooLargeError


def validate_file_size(file_bytes: bytes, max_bytes: int, filename: str) -> None:
    if len(file_bytes) > max_bytes:
        mb = max_bytes / (1024 * 1024)
        raise FileTooLargeError(f"'{filename}' exceeds {mb:.0f} MB limit")
