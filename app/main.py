from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from .router.router_user import router as user_router

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
    openapi_schema["components"] = {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter the access token you received from the /api/users/callback endpoint"
            }
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
app.include_router(user_router)

# Example route
@app.get('/hello')
def hello():
    return {"message": "Hello World"}
