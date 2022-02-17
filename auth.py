import json

import httpx
import jwt as pyjwt
from fastapi import Request
from logger import LoggerFactory

from config import ConfigClass

logger = LoggerFactory(__name__).get_logger()


def jwt_required(request: Request):
    """
        why is there no call to this function?!
        delete candidate!
    """
    token = request.headers.get('Authorization')
    if token:
        token = token.replace("Bearer ", "")
    else:
        raise Exception("Token required")
    payload = pyjwt.decode(token, verify=False)
    username: str = payload.get("preferred_username")

    # check if user is existed in neo4j
    url = ConfigClass.NEO4J_SERVICE_V1 + "nodes/User/query"
    with httpx.Client() as client:
        res = client.post(
            url,
            json={"name": username}
        )
    try:
        res.raise_for_status()
        if res.status_code != 200:
            raise Exception("Neo4j service: " + json.loads(res.text))
    except httpx.HTTPError as exc:
        logger.error("HTTP Exception", exc_info=True)
        raise exc

    users = res.json()
    if not users:
        raise Exception(f"Neo4j service: User {username} does not exist.")
    user_id = users[0]['id']
    role = users[0]['role']
    if username is None:
        raise Exception("User not found")
    return {"user_id": user_id, "username": username, "role": role}
