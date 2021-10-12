def register_routes(api, app,):
    from .controller import api as meta_data_api
    api.add_namespace(meta_data_api, path=f"/v1")