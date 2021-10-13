def register_routes(api, app, root="api"):
    from .controller import api as survey_api
    api.add_namespace(survey_api, path=f"/v1")
    