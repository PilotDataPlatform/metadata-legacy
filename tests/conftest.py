from enum import auto
from re import I
import pytest
import httpx

from fastapi.testclient import TestClient

from config import ConfigClass
from resources.helpers import get_geid


def _delete_workbench_records(project_geid):
    '''
        As soon we don't actually create anything in the neo4j api we should remove this fixture.
    '''
    from app import app
    test_client = TestClient(app)
    response = test_client.get(f"/v1/{project_geid}/workbench")
    for key, value in response.json().get("result").items():
        id = value["id"]
        response = test_client.delete(f"/v1/{project_geid}/workbench/{id}")
    return


def _delete_project(node_id):
    delete_api = ConfigClass.NEO4J_SERVICE_V1 + "nodes/Container/node/%s" % str(node_id)
    with httpx.Client() as client:
        client.delete(delete_api)


@pytest.fixture
def test_client():
    from app import app
    return TestClient(app)


@pytest.fixture
def create_entityinfo_test_project_in_neo4j(scope='session', autouse=True):
    testing_api = ConfigClass.NEO4J_SERVICE_V1 + "nodes/Container"
    params = {
        "name": "EntityInfoUnitTest1",
        "path": 'entityinfo_test_workbench',
        "code": 'entityinfo_test_workbench',
        "description": "Project created by unit test, will be deleted soon...",
        "discoverable": 'true',
        "type": "Usecase",
        "tags": ['test'],
        "global_entity_id": get_geid()
    }
    '''
        ToDo: mock this call. We should have feature tests relay on internet connection or vpn access.
        https://pypi.org/project/pytest-httpx/ its a good lib for external requests testing.
        this would make the test way faster and impossible to break other builds due cleanup error.
    '''
    with httpx.Client() as client:
        res = client.post(testing_api, json=params)
    assert res.status_code == 200
    response_json = res.json()[0]
    yield response_json
    _delete_project(response_json['id'])
    _delete_workbench_records(response_json['global_entity_id'])
