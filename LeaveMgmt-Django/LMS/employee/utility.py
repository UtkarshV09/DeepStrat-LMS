RGL = "RGL"
slant = "/"


def check_code_length(data) -> bool:
    """
    Boolean - > True or False

    """
    if data and len(data) >= 5:
        return True
    return False


def code_format(raw_data) -> str:
    """
    eg. A0091 -> RGLA0091 -> RGL/A0/091
    """

    # Check the existence of data and its length
    if raw_data and len(raw_data.strip()) >= 5:
        raw_data = raw_data.strip().upper()

        # Remove any existing slashes
        raw_data = raw_data.replace("/", "")

        # Insert RGL if it doesn't start with it
        if not raw_data.startswith("RGL"):
            raw_data = "RGL" + raw_data

        # Insert slashes
        formatted_code = raw_data[:3] + "/" + raw_data[3:5] + "/" + raw_data[5:]

        return formatted_code

    else:
        return ""
