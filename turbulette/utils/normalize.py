def camel_to_snake(string: str) -> str:
    """Convert a camel case to snake case

        This as the advantage to only use builtins (no need to import re)

        https://stackoverflow.com/a/44969381/10735573
    Args:
        string (str): The camel case string to convert

    Returns:
        str: The snake case string
    """
    return "".join(["_" + c.lower() if c.isupper() else c for c in string]).lstrip("_")
