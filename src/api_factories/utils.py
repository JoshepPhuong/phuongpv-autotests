import uuid

MAX_NAME_LENGTH = 20


def generate_name_with_uuid(name: str, max_length: int = MAX_NAME_LENGTH) -> str:
    """Generate name with uuid as postfix."""
    return f"{name} {uuid.uuid4().hex}"[:max_length]
