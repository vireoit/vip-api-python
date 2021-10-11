def register_routes(api, app, root="api"):
    from app.api_services import register_routes
    register_routes(api, app)

    from app.masters import register_routes
    register_routes(api, app)

    from app.subjects import register_routes
    register_routes(api, app)
