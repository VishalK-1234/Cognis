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
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(cases.router)   # prefix is inside file
    app.include_router(ufdr.router)    # prefix is inside file
    app.include_router(health.router)  # prefix is inside file

    # Middleware
    app.add_middleware(AuditMiddleware)

    return app

app = create_app()
