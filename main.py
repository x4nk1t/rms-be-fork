from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as AuthRouter
from routes.dashboard import router as DashboardRouter

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
]

app = FastAPI(middleware=middleware)

app.include_router(AuthRouter, prefix="/auth", tags=["auth"])
app.include_router(DashboardRouter, prefix="/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info", loop="none")
