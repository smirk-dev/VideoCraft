from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "working"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
        log_level="info"
    )
