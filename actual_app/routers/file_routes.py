import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import actual_app.database_models as database_models, actual_app.schemas as schemas, actual_app.auth as auth
from actual_app.database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=["Task Files"]
)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE = 1024 * 1024 * 5  # 5MB

@router.post("/{task_id}/upload", response_model=schemas.TaskResponse)
def upload_task_file(
    task_id: int,
    file: UploadFile = File(...),   
    db: Session = Depends(get_db),
    current_user: database_models.User = Depends(auth.get_current_user)
):
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")

    task = db.query(database_models.Task).filter_by(id=task_id, owner_id=current_user.id).first()
 
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
   
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the task")


    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="File is too large")

    import uuid
    unique_prefix = uuid.uuid4().hex
    unique_filename = f"{unique_prefix}_{file.filename}"
    server_save_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(server_save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_file_record = database_models.TaskFile(
        task_id=task_id,
        file_path=server_save_path,
        original_name=file.filename
    )
    db.add(new_file_record)
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_id}/download")
def download_task_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: database_models.User = Depends(auth.get_current_user)
):
    file_record = db.query(database_models.TaskFile).filter(database_models.TaskFile.id==file_id).first()
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if file_record.task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the task")
    if not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing in server storage")
    
    return FileResponse(
        path=file_record.file_path,
        filename=file_record.original_name,
        media_type="application/octet-stream"
    )

@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: database_models.User = Depends(auth.get_current_user)
):
    file_record = db.query(database_models.TaskFile).filter(database_models.TaskFile.id==file_id).first()
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if file_record.task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this file")
    if os.path.exists(file_record.file_path):
        try:
            os.remove(file_record.file_path)
        except OSError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file")
    db.delete(file_record)
    db.commit()
    return None