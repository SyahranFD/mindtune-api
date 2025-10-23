from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .router.router_user import router as user_router

load_dotenv(find_dotenv())

app = FastAPI(title="MindTune API", description="API for MindTune application", version="0.1.0")

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
