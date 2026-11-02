from fastapi import FastAPI

from app.routers import auth
from app.routers import classroom
from app.routers import face
from app.routers import students
from app.routers import voice
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Acadence API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(classroom.router)
app.include_router(face.router)
app.include_router(students.router)
app.include_router(voice.router)


@app.get("/")
def root():
    return {
        "message": "Acadence API is running"
    }