from datetime import datetime
import re

def convert_date_format(date_str):

    primary_format = '%a, %d %b %Y %H:%M:%S %z'
    fallback_format = '%d %b %Y %H:%M:%S %z'

    try:
        parsed_date = datetime.strptime(date_str, primary_format)
    except Exception:
        try:
            parsed_date = datetime.strptime(date_str, fallback_format)
        except Exception:
            return None

    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date

def convert_email_date(date_str):
    date_str = re.sub(r'\s*\([^)]*\)', '', date_str)
    date_str = date_str.replace('GMT', '+0000')
    primary_format = '%a, %d %b %Y %H:%M:%S %z'  # Example: 'Wed, 04 May 2023 17:40:04 +0300'
    fallback_format = '%d %b %Y %H:%M:%S %z'    # Example: '04 May 2023 17:40:04 +0300'

    try:
        parsed_date = datetime.strptime(date_str, primary_format)
    except ValueError:
        try:
            parsed_date = datetime.strptime(date_str, fallback_format)
        except ValueError:
            # If both formats fail, return the generic date
            return None

    formatted_date = parsed_date.strftime('%Y-%m-%d')
    return formatted_date