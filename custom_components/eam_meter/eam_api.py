"""EAM API functions."""
import requests
import re
from datetime import date


def get_session_key(url: str, user: str, pwd: str) -> str:
    """
    Login to the service and extract the session key from the HTML response.

    Args:
        url: The login endpoint URL
        user: Username
        pwd: Password

    Returns:
        Session key extracted from the HTML response

    Raises:
        ValueError: If session key is not found
        requests.RequestException: If the HTTP request fails
    """
    params = {
        "oninputprocessing": (None, "LOGIN$LOGIN"),
        "p": (None, "EAM"),
        "timeout": (None, "86400000"),
        "user": (None, user),
        "passwd": (None, pwd),
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    pattern = r'<input[^>]*id=["\']sessionkey["\'][^>]*value=["\']([A-F0-9]+)["\']'
    match = re.search(pattern, response.text, re.IGNORECASE)

    if not match:
        raise ValueError("Session key not found in response")

    return match.group(1)


def get_selected_read(session_key: str, main_url: str) -> str:
    """
    Get meter metadata from the EAM portal.
    
    Args:
        session_key: The session key from login
        main_url: The main URL
    
    Returns:
        The selected_read value
    
    Raises:
        ValueError: If selected_read value is not found
        requests.RequestException: If the HTTP request fails
    """
    params = {
        'oninputprocessing': (None, 'menu$METER'),
        'p': (None, 'EAM'),
        'sessionkey': (None, session_key)
    }

    response = requests.post(main_url, params=params)
    response.raise_for_status()
    
    selected_pattern = r'<option[^>]*value=["\']([^"\']+)["\'][^>]*selected[^>]*>'
    match = re.search(selected_pattern, response.text, re.IGNORECASE)
    
    if not match:
        raise ValueError("Selected read value not found")
    
    return match.group(1)



def post_readout(session_key: str, selected_read: str, readout_kwh: int, main_url: str) -> bool:
    """
    Post meter readout to the EAM portal.
    
    Args:
        session_key: The session key from login
        selected_read: The selected read value from metadata
        readout_kwh: The meter reading in kWh
        main_url: The main URL
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If readout is invalid
        requests.RequestException: If the HTTP request fails
    """
    if readout_kwh < 0:
        raise ValueError("Readout must be a non-negative integer value")

    if not selected_read:
        raise ValueError("Selected read value is required")
    
    today = date.today().isoformat()
    
    files = {
        'oninputprocessing': (None, 'METER$SICHERN'),
        'p': (None, 'EAM'),
        'sessionkey': (None, session_key),
        'timeout': (None, '1800000'),
        'abl_000000000010323427_001_datum': (None, today),
        'abl_000000000010323427_001_ablesungV': (None, str(readout_kwh)),
        'selected_read': (None, selected_read)
    }
    
    response = requests.post(main_url, files=files)
    response.raise_for_status()

    return response.status_code == 200

def get_last_readout(session_key: str, main_url: str) -> tuple[int, str]:
    """
    Get the last submitted readout from the EAM portal.
    
    Args:
        session_key: The session key from login
        main_url: The main URL

    Returns:
        Tuple of (value: int, date: str) where date is in DD.MM.YYYY format

    Raises:
        ValueError: If last readout value or date is not found
        requests.RequestException: If the HTTP request fails
    """
    params = {
        'oninputprocessing': (None, 'menu$METERHISTORY'),
        'p': (None, 'EAM'),
        'sessionkey': (None, session_key)
    }

    response = requests.post(main_url, params=params)
    response.raise_for_status()
    last_readout_pattern = r'<td class="st-col-other-0 "> *([^<]+) kWh <\/td>'
    kWh_match = re.search(last_readout_pattern, response.text, re.IGNORECASE)
    
    date_pattern = r'<td class="st-col-other-0 "> (\d{2}\.\d{2}\.\d{4}) </td>'
    date_match = re.search(date_pattern, response.text, re.IGNORECASE)

    if not kWh_match:
        raise ValueError("Last readout value not found")
    
    if not date_match:
        raise ValueError("Last readout date not found")
    
    # Parse value as integer
    last_readout_str = kWh_match.group(1).strip().replace(' kWh', '')
    value = int(last_readout_str)
    
    # Get date string in DD.MM.YYYY format
    date_str = date_match.group(1).strip()
    
    return (value, date_str)

    