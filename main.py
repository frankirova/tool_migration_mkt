from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.routes import router

api = FastAPI()

# CORS - config
origins = [
    'http://localhost:5173',
    'http://localhost:8000',
]
api.middleware(
    CORSMiddleware,
    # allow_origins= origins,
    # allow_credentials= True,
    # allow_methods= ['*'],
    # allow_headers= ['*'],
)

api.include_router(router)