from fastapi import FastAPI
from actual_app.database import engine, Base
from actual_app.routers import auth_routes, task_routes, file_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(file_routes.router)
app.include_router(task_routes.router)