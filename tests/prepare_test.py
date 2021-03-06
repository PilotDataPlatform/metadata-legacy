import httpx
from fastapi.testclient import TestClient
from fastapi_sqlalchemy import db

from app import app
from config import ConfigClass
from resources.helpers import get_geid


class SetupException(Exception):
    """Failed setup test."""


class SetUpTest:
    def __init__(self, log):
        self.log = log
        self.app = self.create_test_client()

    def create_test_client(self):
        client = TestClient(app)
        return client

    def create_project(self, code, discoverable='true'):
        self.log.info('\n')
        self.log.info('Preparing testing project'.ljust(80, '-'))
        testing_api = ConfigClass.NEO4J_SERVICE_V1 + 'nodes/Container'
        params = {
            'name': 'EntityInfoUnitTest1',
            'path': code,
            'code': code,
            'description': 'Project created by unit test, will be deleted soon...',
            'discoverable': discoverable,
            'type': 'Usecase',
            'tags': ['test'],
            'global_entity_id': get_geid(),
        }
        self.log.info(f'POST API: {testing_api}')
        self.log.info(f'POST params: {params}')
        try:
            with httpx.Client() as client:
                res = client.post(testing_api, json=params)
            self.log.info(f'RESPONSE DATA: {res.text}')
            self.log.info(f'RESPONSE STATUS: {res.status_code}')
            assert res.status_code == 200
            node = res.json()[0]
            return node
        except Exception as e:
            self.log.info(f'ERROR CREATING PROJECT: {e}')
            raise e

    def delete_project(self, node_id):
        self.log.info('\n')
        self.log.info('Preparing delete project'.ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE_V1 + 'nodes/Container/node/%s' % str(node_id)
        try:
            self.log.info(f'DELETE Project: {node_id}')
            with httpx.Client() as client:
                delete_res = client.delete(delete_api)
            self.log.info(f'DELETE STATUS: {delete_res.status_code}')
            self.log.info(f'DELETE RESPONSE: {delete_res.text}')
        except Exception as e:
            self.log.info(f'ERROR DELETING PROJECT: {e}')
            self.log.info(f'PLEASE DELETE THE PROJECT MANUALLY WITH ID: {node_id}')
            raise e

    def create_file(self, file_event, extra_data={}):
        self.log.info('\n')
        self.log.info('Creating testing file'.ljust(80, '-'))
        filename = file_event.get('filename')
        namespace = file_event.get('namespace')
        project_code = file_event.get('project_code')
        project_id = file_event.get('project_id')
        with httpx.Client() as client:
            geid_res = client.get(ConfigClass.UTILITY_SERVICE_V1 + 'utility/id')
        self.log.info(f'Getting global entity ID: {geid_res.text}')
        global_entity_id = geid_res.json()['result']
        if namespace.lower() == 'core':
            namespace_label = 'Core'
        else:
            namespace_label = 'Greenroom'
        payload = {
            'file_size': 1000,
            'display_path': filename,
            'location': f'minio://http://unittest/{project_code}/{filename}',
            'dcm_id': 'undefined',
            'guid': 'unittest_guid',
            'namespace': namespace,
            'uploader': 'unittest',
            'project_id': project_id,
            'name': filename,
            'input_file_id': global_entity_id,
            'process_pipeline': 'raw',
            'operator': 'entity_info_unittest',
            'tags': ['tag1', 'tag2'],
            'global_entity_id': global_entity_id,
            'parent_folder_geid': 'None',
            'project_code': project_code,
            'extra_labels': [namespace_label],
        }
        if extra_data:
            payload = {**payload, **extra_data}
        testing_api = ConfigClass.NEO4J_SERVICE_V1 + 'nodes/File'
        self.log.info(f'File create payload {payload}')
        try:
            self.log.info(f'POST API: {testing_api}')
            self.log.info(f'POST payload: {payload}')
            with httpx.Client() as client:
                res = client.post(testing_api, json=payload)
            self.log.info(f'RESPONSE DATA: {res.text}')
            self.log.info(f'RESPONSE STATUS: {res.status_code}')
            assert res.status_code == 200
            result = res.json()[0]
            file_id = result.get('id')
            relation_payload = {'start_id': project_id, 'end_id': file_id}
            relation_api = ConfigClass.NEO4J_SERVICE_V1 + 'relations/own'
            with httpx.Client() as client:
                relation_res = client.post(relation_api, json=relation_payload)
            self.log.info(f'Create relation res: {relation_res.text}')

            # get folder id by geid
            if file_event.get('parent_geid'):
                folder_query = {'global_entity_id': file_event.get('parent_geid')}
                with httpx.Client() as client:
                    response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'nodes/Folder/query', json=folder_query)
                folder_node = response.json()[0]
                relation_payload = {'start_id': folder_node['id'], 'end_id': file_id}
                relation_api = ConfigClass.NEO4J_SERVICE_V1 + 'relations/own'
                with httpx.Client() as client:
                    relation_res = client.post(relation_api, json=relation_payload)
                self.log.info(f'Create relation res: {relation_res.text}')
            return result
        except Exception as e:
            self.log.info(f'ERROR CREATING FILE: {e}')
            raise e

    def create_folder(self, geid, project_code):
        self.log.info('\n')
        self.log.info('Creating testing folder'.ljust(80, '-'))
        payload = {
            'global_entity_id': geid,
            'folder_name': 'entityinfo_unittest_folder',
            'folder_level': 0,
            'uploader': 'EntityInfoUnittest',
            'folder_relative_path': '',
            'zone': 'greenroom',
            'project_code': project_code,
            'folder_tags': [],
            'folder_parent_geid': '',
            'folder_parent_name': '',
        }
        testing_api = '/v1/folders'
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f'RESPONSE DATA: {res.text}')
            self.log.info(f'RESPONSE STATUS: {res.status_code}')
            assert res.status_code == 200
            result = res.json().get('result')
            return result
        except Exception as e:
            self.log.info(f'ERROR CREATING FOLDER: {e}')
            raise e

    def delete_folder_node(self, node_id):
        self.log.info('\n')
        self.log.info('Preparing delete folder node'.ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE_V1 + 'nodes/Folder/node/%s' % str(node_id)
        try:
            with httpx.Client() as client:
                delete_res = client.delete(delete_api)
            self.log.info(f'DELETE STATUS: {delete_res.status_code}')
            self.log.info(f'DELETE RESPONSE: {delete_res.text}')
        except Exception as e:
            self.log.info(f'ERROR DELETING FILE: {e}')
            self.log.info(f'PLEASE DELETE THE FILE MANUALLY WITH ID: {node_id}')
            raise e

    def delete_file_node(self, node_id):
        self.log.info('\n')
        self.log.info('Preparing delete file node'.ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE_V1 + 'nodes/File/node/%s' % str(node_id)
        try:
            with httpx.Client() as client:
                delete_res = client.delete(delete_api)
            self.log.info(f'DELETE STATUS: {delete_res.status_code}')
            self.log.info(f'DELETE RESPONSE: {delete_res.text}')
        except Exception as e:
            self.log.info(f'ERROR DELETING FILE: {e}')
            self.log.info(f'PLEASE DELETE THE FILE MANUALLY WITH ID: {node_id}')
            raise e

    def delete_file_entity(self, guid):
        self.log.info('\n')
        self.log.info('Preparing delete file entity'.ljust(80, '-'))
        delete_api = ConfigClass.CATALOGUING + '/v1/entity/guid/' + str(guid)
        try:
            with httpx.Client() as client:
                delete_res = client.delete(delete_api)
            self.log.info(f'DELETE STATUS: {delete_res.status_code}')
            self.log.info(f'DELETE RESPONSE: {delete_res.text}')
        except Exception as e:
            self.log.info(f'ERROR DELETING FILE: {e}')
            self.log.info(f'PLEASE DELETE THE FILE MANUALLY WITH GUID: {guid}')
            raise e

    def delete_workbench_records(self, project_geid):
        response = self.app.get(f'/v1/{project_geid}/workbench')
        if response.status_code != 200:
            self.log.info('ERROR DELETING WORKBENCH SQL ENTRY')
        for key, value in response.json().get('result').items():
            id = value['id']
            response = self.app.delete(f'/v1/{project_geid}/workbench/{id}')
        return

    def delete_manifest(self, manifest_id):
        response = self.app.delete(f'/v1/manifest/{manifest_id}')
        if response.status_code != 200:
            self.log.info('ERROR DELETING MANIFEST SQL ENTRY')

    def get_data_manifests(self, project_code):
        response = self.app.get(f'/v1/manifests?project_code={project_code}')
        if response.status_code != 200:
            self.log.info('Error while getting data manifest')
        res = response.json()['result']

        return res

    def get_project_details(self, project_code):
        try:
            url = ConfigClass.NEO4J_SERVICE_V1 + 'nodes/Container/query'
            with httpx.Client() as client:
                response = client.post(url, json={'code': project_code})
            if response.status_code == 200:
                response = response.json()
                return response
        except Exception as error:
            self.log.info(f'ERROR WHILE GETTING PROJECT: {error}')
            raise error
