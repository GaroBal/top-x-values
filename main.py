from fastapi import FastAPI

from app.handler import router

app = FastAPI(title="Top Values API")

# Include router
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",  # use string reference to app instead of app directly
        host="0.0.0.0",
        port=8000,
        reload=True,  # enable auto-reload
    )
