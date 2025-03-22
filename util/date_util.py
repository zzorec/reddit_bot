from datetime import datetime

import pytz


# Can be used to format date to club's local timezone and user-friendly format.
def format_date(date, short, include_year) -> str:
    timezone = pytz.timezone("Europe/Rome")
    date_time = datetime.fromisoformat(date).astimezone(timezone)
    if short:
        if include_year:
            return date_time.strftime("%d %b %Y")
        else:
            return date_time.strftime("%d %b")
    else:
        if include_year:
            return date_time.strftime("%A, %d %B %Y")
        else:
            return date_time.strftime("%A, %d %B")


# Can be used to format time to club's local timezone and user-friendly format.
def format_time(time_value) -> str:
    timezone = pytz.timezone("Europe/Rome")
    date = datetime.fromisoformat(time_value).astimezone(timezone)
    return date.strftime("%H:%M")


# Used for sending the active season information to the API.
def get_active_season(current_date=None):
    if current_date is None:
        current_date = datetime.today()
    return current_date.year - 1 if current_date.month <= 7 else current_date.year


if __name__ == "__main__":
    pass
