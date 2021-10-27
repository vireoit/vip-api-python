def register_routes(api, app, root="api"):
    from .controller import api as settings_api
    api.add_namespace(settings_api, path=f"/v1")