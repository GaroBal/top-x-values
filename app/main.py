from fastapi import FastAPI

app = FastAPI()


# Root endpoint
@app.get("/ping")
def get():
    return {"pong"}
