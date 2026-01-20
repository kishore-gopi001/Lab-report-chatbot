from fastapi import FastAPI # type: ignore

app = FastAPI(
    title="Lab Report Interpretation System",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
