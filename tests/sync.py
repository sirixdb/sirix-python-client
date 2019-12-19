import re
import json


def register(requests_mock):
    # mock auth
    def match_body_auth(request):
        print(request.text)
        return (
            "username" in (request.text or "")
            and "password" in (request.text or "")
            and "grant_type" in (request.text or "")
        )

    requests_mock.post(
        re.compile(".+/token"),
        additional_matcher=match_body_auth,
        content=json.dumps(
            {"access_token": "Bearer asdlfiohae5r4", "refresh_token": "987432asdfa312e"}
        ).encode("utf-8"),
    )
    # mock resources endpoint
    requests_mock.get(
        "/?withResources=true",
        content=json.dumps(
            {
                "databases": [
                    {
                        "name": "Create Database By Index!",
                        "type": "json",
                        "resources": ["{'amazingly': 'easy'}"],
                    }
                ]
            }
        ).encode("utf-8"),
    )
