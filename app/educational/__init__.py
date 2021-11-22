def register_routes(api, app, root="api"):
    from .controller import api as educational_api
    api.add_namespace(educational_api, path=f"/v1")