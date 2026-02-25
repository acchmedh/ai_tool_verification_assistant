import datetime


def get_current_date():
    return datetime.datetime.now()


def add_days_to_date(date_str, days):
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    new_date = date_obj + datetime.timedelta(days=days)
    return new_date.strftime("%Y-%m-%d")
