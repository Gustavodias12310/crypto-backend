from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "API rodando"}

@app.get("/status")
def status():
    return {"ok": True}
