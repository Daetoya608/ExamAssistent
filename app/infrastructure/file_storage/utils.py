
def get_key(filename: str, folder: str = "/"):
    if len(folder) == 0 or folder[-1] != "/":
        folder += "/"
    key = f"{folder}{filename}"
    return key
