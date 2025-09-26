from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import auth, users, cases, ufdr, health
from app.middleware.audit import AuditMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="Cognis",
        description="AI-based UFDR Analysis Tool",
        version="1.0.0",
    )

    # Routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(cases.router)
    app.include_router(ufdr.router)
    app.include_router(health.router)

    # Middleware
    app.add_middleware(AuditMiddleware)

    # 👉 Add this to print all registered routes
    for route in app.routes:
        print(f"{route.methods} -> {route.path}")

    return app

app = create_app()