from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi

from .router.router_user import router_user

load_dotenv(find_dotenv())

app = FastAPI(title="MindTune API", description="API for MindTune application", version="0.1.0")

# Configure OpenAPI with security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme for Bearer token
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
        
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter the access token you received from the /api/users/access-token endpoint"
        }
    }
    
    # Apply security globally to all endpoints
    openapi_schema["security"] = [{"Bearer": []}]
    
    # Pastikan semua path memiliki security yang konsisten
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            if isinstance(method, dict):
                # Skip login dan callback endpoints
                if method.get("operationId") not in ["login", "callback"]:
                    method["security"] = [{"Bearer": []}]
                    
                # Hapus parameter authorization dari dokumentasi
                if "parameters" in method:
                    method["parameters"] = [param for param in method["parameters"] 
                    if not (param.get("name") == "authorization" and param.get("in") == "header")]
                    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint with redirect to docs
@app.get('/', response_class=RedirectResponse, include_in_schema=False)
def docs():
    return RedirectResponse(url='/docs')

# Include routers
app.include_router(router_user, prefix="/api/users", tags=["Users"])

