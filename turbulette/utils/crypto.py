from random import SystemRandom


def get_random_string(size: int, allowed_chars: tuple):
    """Generate a cryptographically random string

    From this answer :
    https://stackoverflow.com/a/23728630/10735573

    Args:
        size (int): string length

    Returns:
        (string): The random string
    """
    return "".join(SystemRandom().choice(allowed_chars) for _ in range(size))
