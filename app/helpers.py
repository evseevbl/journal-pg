def date_str(date):
    return f'{date.day} {rus_month(date.month)}'


def rus_month(m):
    return [
        'января',
        'декабря',
        'февраля',
        'марта',
        'апреля',
        'мая',
        'июня',
        'июля',
        'августа',
        'сентября',
        'октября',
        'ноября',
        'декабря',
    ][m]
