from pydantic import Field
from models.base_models import APIResponse

class StatsResponse(APIResponse):
    """
    System Metrics/Stats Response Class
    """
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "result":
            {
                "active_user": 20,
                "project": 20,
                "storage": 250,
                "vm": 30,
                "cores": 20,
                "ram": 80,
                "date": "2022-01-12"
            }
    }
                         )
