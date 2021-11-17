def register_routes(api, app, root="api"):
    from .controller import api as general_api
    api.add_namespace(general_api, path=f"/v1")

