# UPLOAD-API
This API is a python fastAPI designed to load Neo4j dumps/backups from an S3 bucket.

## Documentation
Following routes are available:
#### Task request
```json
POST /
With JSON body as followed:
{
    "dbName": "string",
    "s3_url": "string",
    "s3_region": "string"
}
```
#### Task response
```json 
{
"message":"Process started. Please check '/getStatus' to check the status of your request.",
"id":"string"
}
```
#### Status request
```json
POST /getStatus
With JSON body as followed:
{
    "task_id": "string"
}
```
#### Status response
```json
{"task_id":"xxx","status":"in progress|failed|completed"}
```

## Testing

#### Task request
```shell
curl -X 'POST' \
  'http://localhost:8000/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "dbName": "example-db",
  "s3_url": "s3://neo4jmorgan/neo4j-2023-10-12T21-25-24.backup",
  "s3_region": "eu-west-2"
}'
```

#### Task response
```json
{
    "message":"Process started. Please check '/getStatus' to check the status of your request.",
    "id":"5b60f5d1-3c44-4bc4-a05a-02d9add21171"
}
```

#### Status request
```shell
curl -X 'POST' \
  'http://localhost:8000/getStatus' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "task_id": "5b60f5d1-3c44-4bc4-a05a-02d9add21171"
}'
```

#### Status response
```json
{
    "task_id":"5b60f5d1-3c44-4bc4-a05a-02d9add21171",
    "status":"completed"
}
```
