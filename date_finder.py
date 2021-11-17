import datetime

dates = {}
def find_dates():
    dates['today'] = datetime.date.today()
    dates['yesterday'] = datetime.date.today()-datetime.timedelta(1)

    return dates
