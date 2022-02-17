from typing import Optional

from fastapi import APIRouter
from fastapi_sqlalchemy import db
from fastapi_utils.cbv import cbv
from logger import LoggerFactory
from sqlalchemy import cast
from sqlalchemy import Date
from sqlalchemy import func

from models.base_models import EAPIResponseCode
from models.metrics import StatsResponse
from models.metrics_sql import SystemMetrics

router = APIRouter()
_API_NAMESPACE = "stats_restful"


@cbv(router)
class SystemStats:

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/stats",
                response_model=StatsResponse,
                summary="Retrieve System Stats/Metrics")
    async def get_metrics(self, date: Optional[str] = None):
        '''
        Retrieve all metrics from opsdb table
        '''

        self._logger.info("API system_metrics".center(80, '-'))
        api_response = StatsResponse()

        try:
            # if date query parameter not provided, query the most recent date
            if date is None:
                response_query = db.session.query(SystemMetrics.active_user,SystemMetrics.project, SystemMetrics.storage,
                    SystemMetrics.vm, SystemMetrics.cores,SystemMetrics.ram, func.to_char(SystemMetrics.date, 'YYYY-MM-DD')). \
                    order_by(SystemMetrics.date.desc()).first()

            # if date provided with parameter, query selected date
            else:
                response_query = db.session.query(SystemMetrics.active_user, SystemMetrics.project, SystemMetrics.storage,
                    SystemMetrics.vm, SystemMetrics.cores, SystemMetrics.ram, func.to_char(SystemMetrics.date, 'YYYY-MM-DD')). \
                    filter(cast(SystemMetrics.date, Date) == date).first()

            if response_query is None:
                raise Exception("Failure to query metrics from database table")

            # convert query into dict for response
            response_columns = ["active_user", "project", "storage", "vm", "cores", "ram", "date"]
            response_info = dict(zip(response_columns, response_query))

            self._logger.info(f"Most recent system metrics retrieved are: {response_info}")
            api_response.result = response_info
            api_response.error_msg = ""
            api_response.code = EAPIResponseCode.success
            return api_response.json_response()

        except Exception as e:
            api_response.result = []
            error_msg = str(e)
            error = f"Retrieval of metrics failed: {error_msg}"
            api_response.error_msg = error
            self._logger.error(error)
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
