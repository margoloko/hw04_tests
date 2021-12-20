from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    now = date.today()
    year = now.strftime('%Y')
    return {'year': int(year)}
