from contextlib import contextmanager
import httpx


@contextmanager
def include_response_text_in_errors():
    try:
        yield
    except httpx.HTTPError as exc:
        response = exc.response
        message = f"{exc}\nSirixDB error message: {response.text}"
        raise SirixServerError(message, response=response) from None


class SirixServerError(httpx.HTTPError):
    pass
