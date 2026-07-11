from fastapi import FastAPI

app = FastAPI(
    title="MarketFlow Activity Service",
    description="Records important marketplace events.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "MarketFlow Activity Service is running. Go to /docs"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}