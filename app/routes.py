def register_routes(api, app, root="api"):
    from app.api_services import register_routes
    register_routes(api, app)


