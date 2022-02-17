from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from logger import LoggerFactory

import models.files as files_models
import models.project as project_models
from models.base_models import APIResponse
from models.base_models import EAPIResponseCode
from resources.error_handler import catch_internal
from resources.helpers import get_file_count_neo4j
from resources.helpers import get_operation_logs_total

router = APIRouter()
_API_NAMESPACE = "api_files_stats"


@cbv(router)
class FilesStats:
    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.get('/project/{project_geid}/files/statistics', response_model=files_models.FilesStatsGETResponse,
                summary="FilesDailyStats Restful")
    @catch_internal(_API_NAMESPACE)
    def get(self, project_geid, start_date, end_date, operator=None):
        '''
        Get function to extract daily file statistics
        '''
        # /v1/audit-logs/ {"project_code":"0407","start_date":1618200000,"end_date":1618286399,"resource":"file"}
        self._logger.info(
            f"FilesDailyStats project_geid: {project_geid}")
        api_response = APIResponse()
        api_response.code = EAPIResponseCode.success
        # get project
        project_info = project_models.http_query_node({
            "global_entity_id": project_geid
        }).json()[0]
        # get stats from auditlogs
        stats_from_auditlogs = [get_operation_logs_total(
            project_info['code'],
            operation_type,
            start_date,
            end_date,
            "file",
            operator=operator
        ) for operation_type in ["data_upload", "data_download", "data_transfer"]]
        # get stats from neo4j count
        stats_from_neo4j = [get_file_count_neo4j(
            project_info['code'],
            zone,
            uploader=operator
        ) for zone in ["Greenroom", "Core"]]
        # return response
        api_response.result = {
            "uploaded": stats_from_auditlogs[0],
            "downloaded": stats_from_auditlogs[1],
            "approved": stats_from_auditlogs[2],
            "greenroom": stats_from_neo4j[0],
            "core": stats_from_neo4j[1],
            "project_info": project_info
        }
        return api_response.json_response()
