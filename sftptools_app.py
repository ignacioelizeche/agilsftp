from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.sftp_service import download_from_server
from fastapi.responses import Response
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()  # carga variables del .env

BASE_DOWNLOAD_PATH = os.getenv("BASE_DOWNLOAD_PATH", "C:/Users/adminlambare/agilsftp")

app = FastAPI(title="SFTP/FTPS Tools API")

class ServerRequest(BaseModel):
    host: str
    directory: str
    destination_folder: str
    username: str
    password: str
    filename_startswith: Optional[List[str]] = None
    from_date: Optional[str] = ""
    port: Optional[int] = None
    conn_type: Optional[str] = "sftp"

@app.post("/servercopy")
async def server_copy(request: ServerRequest):
    try:
        download_path = os.path.join(BASE_DOWNLOAD_PATH, os.path.basename(request.destination_folder))
        os.makedirs(download_path, exist_ok=True)

        zip_buffer = download_from_server(
            host=request.host,
            username=request.username,
            password=request.password,
            directory=request.directory,
            download_path=download_path,
            filename_startswith=request.filename_startswith or [],
            from_date=request.from_date,
            port=request.port,
            conn_type=request.conn_type
        )

        headers = {"Content-Disposition": f"attachment; filename={request.destination_folder}_archivos.zip"}
        zip_buffer.seek(0)
        return Response(content=zip_buffer.read(), media_type="application/zip", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
