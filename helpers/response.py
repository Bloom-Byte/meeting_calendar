from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def response_message(
        request: HttpRequest, 
        title: str = None,
        content: str = None,
        status: int = 200
    ) -> HttpResponse:
    """
    Renders a message to the authenticated user with the given title and content.

    :param request: The request object.
    :param title: The title of the message.
    :param content: The content of the message.
    :param status: The status code of the response.
    :return: The response object.
    """
    context = {
        "title": title,
        "content": content,
        "type": "info" if status == 200 else "error"
    }
    if not request.user.is_authenticated:
        raise PermissionError("User must be authenticated to view this message.")
    return render(request, "base/message.html", context, status=status)
