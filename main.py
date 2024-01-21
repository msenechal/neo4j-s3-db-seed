from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os
from neo4j import AsyncGraphDatabase
import uuid

app = FastAPI()

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

# If you need retention on the completed/failed tasks (if pod crash etc), consider storing it somewhere (like in redis or other)
task_status = {}

class UploadRequest(BaseModel):
    dbName: str
    s3_url: str
    s3_region: str

class StatusRequest(BaseModel):
    task_id: str

async def neo4j_db_seed(task_id: str, dbName: str, s3_url: str, s3_region: str):
    print(f"Starting task {task_id}")
    try:
        driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        session = driver.session()
        Query = "CREATE DATABASE $dbName OPTIONS {existingData: 'use', seedURI: $seedURI, seedConfig: 'region="+s3_region+"'}"
        await session.run(Query, dbName=dbName, seedURI=s3_url)
        task_status[task_id] = "completed"
        print(f"Task {task_id} completed")
    except Exception as e:
        task_status[task_id] = "failed"
        print(f"Task {task_id} failed with error {e}")
        session.cancel()
        raise
    finally:
        await session.close()

@app.post("/")
async def upload_dump(background_tasks: BackgroundTasks, request: UploadRequest):
    # Seed the cluster with the graph we just loaded
    task_id = str(uuid.uuid4())
    task_status[task_id] = "in progress"
    background_tasks.add_task(neo4j_db_seed, task_id, request.dbName, request.s3_url, request.s3_region)
    return {"message": "Process started. Please check '/getStatus' to check the status of your request.", "id": task_id}

@app.post("/getStatus")
async def get_status(request: StatusRequest):
    status = task_status.get(request.task_id, "Task not found")
    return {"task_id": request.task_id, "status": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
