def register_routes(api, app, root="api"):

    from app.subjects import register_routes
    register_routes(api, app)

    from app.surveys import register_routes
    register_routes(api, app)

    from app.home import register_routes
    register_routes(api, app)

    from app.masters import register_routes
    register_routes(api, app)

    from app.insights import register_routes
    register_routes(api, app)

    from app.audit import register_routes
    register_routes(api, app)

    from app.settings import register_routes
    register_routes(api, app)

    from app.general import register_routes
    register_routes(api, app)

    from app.educational import register_routes
    register_routes(api, app)

