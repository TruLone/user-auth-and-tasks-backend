from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import actual_app.database_models as database_models, actual_app.schemas as schemas
from actual_app.database import get_db
from actual_app.auth import get_current_user
import os

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_input: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: database_models.User = Depends(get_current_user)
):
    new_task = database_models.Task(**task_input.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[schemas.TaskResponse])
def get_user_tasks(
    db: Session = Depends(get_db),
    current_user: database_models.User = Depends(get_current_user)
):
    tasks = db.query(database_models.Task).filter_by(owner_id=current_user.id).all()
    return tasks

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_input: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: database_models.User = Depends(get_current_user)
):
    task = db.query(database_models.Task).filter_by(id=task_id, owner_id=current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the task")
    for key, value in task_input.model_dump().items():
        if value is not None:
            setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: database_models.User = Depends(get_current_user)
):
    task = db.query(database_models.Task).filter_by(id=task_id, owner_id=current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the task")
    
    for attachment in task.attachments:
        if os.path.exists(attachment.file_path):
            try:
                os.remove(attachment.file_path)
            except OSError:
                pass
    db.delete(task)
    db.commit()
    return None