from config import ConfigClass
import httpx


def get_geid():
    '''
    get geid
    http://localhost:5062/v1/utility/id?entity_type=data_upload
    '''
    url = ConfigClass.UTILITY_SERVICE_V1 + \
        "utility/id"
    with httpx.Client() as client:
        response = client.get(url)
    if response.status_code == 200:
        return response.json()['result']
    else:
        raise Exception('get_geid {}: {}'.format(response.status_code, url))


def get_operation_auditlogs(project_code, action,
                            start_date, end_date, resource, operator=None, ):
    '''
    get operation auditlogs from service_provenance
    '''
    url = ConfigClass.PROVENANCE_SERVICE_V1 + "audit-logs"
    params = {
        "project_code": project_code,
        "action": action,
        "start_date": start_date,
        "end_date": end_date,
        "page_size": 50
    }
    if resource:
        params['resource'] = resource
    if operator:
        params['operator'] = operator
    with httpx.Client() as client:
        response = client.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']
    else:
        raise Exception('get_operation_auditlogs {}: {}'.format(
            response.status_code, url))

def get_operation_logs_total(project_code, action,
                            start_date, end_date, resource, operator=None, ):
    '''
    get operation auditlogs total from service_provenance
    '''
    url = ConfigClass.PROVENANCE_SERVICE_V1 + "audit-logs"
    params = {
        "project_code": project_code,
        "action": action,
        "start_date": start_date,
        "end_date": end_date,
        "page_size": 1
    }
    if resource:
        params['resource'] = resource
    if operator:
        params['operator'] = operator
    with httpx.Client() as client:
        response = client.get(url, params=params)
    if response.status_code == 200:
        return response.json()['total']
    else:
        raise Exception('get_operation_auditlogs {}: {}'.format(
            response.status_code, url))

def get_file_count_neo4j(project_code, zone, archived=False, uploader=None):
    url = ConfigClass.NEO4J_SERVICE_V1 + "file/quick/count"
    labels = {
        "Greenroom": "Greenroom:File",
        "Core": "Core:File"
    }.get(zone)
    params = {
        "labels": labels,
        "project_code": str(project_code),
        'archived': '[bool]True' if archived else '[bool]False'
    }
    if uploader:
        params["display_path"] = uploader
        params["startwith"] = ["display_path"]
    with httpx.Client() as client:
        response = client.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']
    else:
        raise Exception('get_file_count_neo4j {}: {}'.format(
            response.status_code, url))
