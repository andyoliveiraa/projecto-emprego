import asyncio
import uvicorn
from web import app
from worker import worker_loop

@app.on_event("startup")
async def startup_event():
    # Inicia o ciclo de extração e IA em background assim que o servidor web arranca
    asyncio.create_task(worker_loop())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
