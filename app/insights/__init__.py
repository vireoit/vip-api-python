def register_routes(api, app, root="api"):
    from .controller import api as insights_api
    api.add_namespace(insights_api, path=f"/v1")