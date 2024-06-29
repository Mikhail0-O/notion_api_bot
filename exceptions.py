class RequestError(Exception):
    """Неизвестная ошибка HTTP-запроса."""

    pass


class RequestLimitError(Exception):
    """Превышен лимит запросов. Ошибка 429."""

    pass
