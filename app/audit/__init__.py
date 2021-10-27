def register_routes(api, app, root="api"):
    from .controller import api as audit_api
    api.add_namespace(audit_api, path=f"/v1")
