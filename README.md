# MDIP API

The Medications Data Interoperability Project (MDIP) is funded project conducted by Dynaccurate and Pillcheck to create a large scale database of linked medications sourced from the EU, Canada, UK and USA which will flag medications associated with potential pharmacogenomic impacts.

## Environment Variables

Below are the required and optional environment variables for running the project. These should be set in a `.env` file at the project root.

### Core Environment Variables

| Variable                  | Required | Description                                                       |
|---------------------------|----------|-------------------------------------------------------------------|
| `ENVIRONMENT`             | Yes      | Application environment. Options: `PROD`, `DEV`, `TEST`.          |
| `RABBITMQ_URL`            | Yes      | RabbitMQ connection string.                                       |
| `DATABASE_URL`            | Yes      | PostgreSQL connection string.                                     |
| `DATABASE_ECHO`           | No       | Enable SQLAlchemy echo (SQL debug logs). Default: `False`.        |
| `CORS_ORIGINS`            | No       | Allowed CORS origins. Default: `[*]`.                             |
| `CORS_HEADERS`            | No       | Allowed CORS headers. Default: `[*]`.                             |
| `CORS_METHODS`            | No       | Allowed CORS methods. Default: `[*]`.                             |
| `JWT_SECRET`              | No       | JWT secret key. Default: `thisissecret`.                          |
| `JWT_ACCESS_EXPIRATION`   | No       | JWT access token expiration (seconds). Default: `900` (15 min).   |
| `JWT_REFRESH_EXPIRATION`  | No       | JWT refresh token expiration (seconds). Default: `1800` (30 min). |

### Azure Confidential Ledger (Required in PROD)

| Variable                            | Required  | Description                                           |
|-------------------------------------|-----------|-------------------------------------------------------|
| `AZURE_LEDGER_URL`                  | Yes       | Azure Confidential Ledger endpoint URL.               |
| `AZURE_LEDGER_CERTIFICATE_PATH`     | Yes       | Path to the Azure Ledger certificate file.            |
| `AZURE_CREDENTIAL_TENNANT_ID`       | Yes       | Azure AD Tenant ID for authentication.                |
| `AZURE_CREDENTIAL_CLIENT_ID`        | Yes       | Azure AD Client ID for authentication.                |
| `AZURE_CREDENTIAL_CERTIFICATE_PATH` | Yes       | Path to the Azure AD authentication certificate file. |

### File Upload Strategy

| Variable                               | Required    | Description                                                 |
|----------------------------------------|-------------|-------------------------------------------------------------|
| `UPLOAD_STRATEGY`                      | Yes         | File upload strategy. Options: `DISK`, `AZURE`.             |
| `DOCUMENTS_STORAGE_PATH`               | Yes (DISK)  | Local path for storing documents (if `DISK` strategy).      |
| `AZURE_BLOB_CONTAINER_NAME`            | Yes (AZURE) | Azure Blob Storage container name (if `AZURE` strategy).    |
| `AZURE_BLOB_STORAGE_CONNECTION_STRING` | Yes (AZURE) | Azure Blob Storage connection string (if `AZURE` strategy). |

## Running the Project

### 1. Install Dependencies

```bash
poetry install
```

### 2. Set Up Environment Variables

- Create a `.env` file and fill with the required values listed above.

### 3. Run Database Migrations

```bash
poetry run task auhead
```

### 4. Start the API Server

```bash
poetry run task run
```

The API docs will be available at [http://localhost:8000/api/docs](http://localhost:8000/api/docs) and [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc).

### 5. Run the Task Workers

```bash
poetry run task run-worker
```

## Testing

To run tests:

```bash
poetry run pytest .
```

## License

This project is maintained by Dynaccurate. For licensing details, see the repository or contact the author.
