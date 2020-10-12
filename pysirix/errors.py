from contextlib import contextmanager
import httpx


@contextmanager
def include_response_text_in_errors():
    try:
        yield
    except httpx.HTTPStatusError as exc:
        response = exc.response
        message = f"{exc}\nSirixDB error message: {response.text}"
        raise SirixServerError(message, response=response, request=exc.request) from None


class SirixServerError(httpx.HTTPStatusError):
    pass
