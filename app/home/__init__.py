def register_routes(api, app, root="api"):
    from .controller import api as home_api
    api.add_namespace(subject_api, path=f"/v1")