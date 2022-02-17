from fastapi_sqlalchemy import db
from models.manifest_sql import DataManifestModel , DataAttributeModel

class Manifest:

    @classmethod
    def get_by_project_name(cls, project_code):
        manifests = db.session.query(DataManifestModel).filter_by(project_code=project_code)
        results = []
        for manifest in manifests:
            result = manifest.to_dict()
            result["attributes"] = []
            attributes = db.session.query(DataAttributeModel).filter_by(
                manifest_id=manifest.id
            ).order_by(DataAttributeModel.id.asc())
            for atr in attributes:
                result["attributes"].append(atr.to_dict())
            results.append(result)
        return results

    @classmethod
    def get_by_id(cls, id):
        manifest = db.session.query(DataManifestModel).get(id)
        if manifest:
            result = manifest.to_dict()
            result["attributes"] = []
            attributes = db.session.query(DataAttributeModel).filter_by(
                manifest_id=id
            ).order_by(DataAttributeModel.id.asc())
            for atr in attributes:
                result["attributes"].append(atr.to_dict())
            return result
        return None