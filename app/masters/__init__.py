def register_routes(api, app, root="api"):
    from .controller import api as masters_api
    api.add_namespace(masters_api, path=f"/v1")
