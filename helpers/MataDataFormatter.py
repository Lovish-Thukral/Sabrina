def format_user_metadata(meta: dict, request: str) -> str:
    lines = ['KNOWN USER INFO']
    user = meta.get("user", {})
    prefs = meta.get("preferences", {})

    if (user and request == "user"):
        lines.append(f"- Name: {user.get('name', 'Unknown')}")
        lines.append(f"- Operating System : {user.get('user_os', 'unknown')}")
        lines.append(f"- Operating System : {user.get('user_os', 'unknown')}")
        lines.append(f"- Default Shell: {user.get('default_shell', 'unknown')}")

    if (prefs and request == "preferences"):
        lines.append(f"- Response style: {prefs.get('response_style')}")
        lines.append(f"- Verbosity: {prefs.get('verbosity')}")

    return "\n".join(lines)
