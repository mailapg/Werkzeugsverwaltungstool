import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.schemas.tool import ToolCreate, ToolUpdate, ToolRead
from src.app.models.tool import Tool
import src.app.crud.tool as crud

UPLOAD_DIR = Path("static/tool_images")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

router = APIRouter(tags=["Tools"])


def _save_image(tool: Tool, file: UploadFile, db: Session) -> None:
    """Speichert eine Bilddatei auf der Festplatte und aktualisiert die DB."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Nur Bilddateien erlaubt (jpeg, png, webp, gif)")
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{tool.id}_{uuid.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if tool.image_filename:
        old = UPLOAD_DIR / tool.image_filename
        if old.exists():
            old.unlink()
    (UPLOAD_DIR / filename).write_bytes(file.file.read())
    crud.set_tool_image(db, tool, filename)


@router.get("/gettools", response_model=list[ToolRead],
            dependencies=[Depends(get_current_user)])
def list_tools(
    db: Session = Depends(get_db),
    name: Optional[str] = None,
    category_id: Optional[int] = None,
):
    return crud.get_tools(db, name=name, category_id=category_id)


@router.get("/gettool/{tool_id}", response_model=ToolRead,
            dependencies=[Depends(get_current_user)])
def get_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.post("/createtool", response_model=ToolRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_tool(
    tool_name: str = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    data = ToolCreate(tool_name=tool_name, description=description, category_id=category_id)
    tool = crud.create_tool(db, data)
    if image and image.filename:
        _save_image(tool, image, db)
        db.refresh(tool)
    return tool


@router.patch("/updatetool/{tool_id}", response_model=ToolRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_tool(
    tool_id: int,
    tool_name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    update_fields = {}
    if tool_name is not None:
        update_fields["tool_name"] = tool_name
    if description is not None:
        update_fields["description"] = description
    if category_id is not None:
        update_fields["category_id"] = category_id
    tool = crud.update_tool(db, tool, ToolUpdate(**update_fields))
    if image and image.filename:
        _save_image(tool, image, db)
        db.refresh(tool)
    return tool


@router.delete("/deletetool/{tool_id}", status_code=200,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    name = tool.tool_name
    crud.delete_tool(db, tool)
    return {"message": f"Werkzeug '{name}' wurde gelöscht", "id": tool_id}


@router.post("/uploadtoolimage/{tool_id}", response_model=ToolRead,
             dependencies=[Depends(require_role("ADMIN"))])
def upload_tool_image(tool_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    _save_image(tool, file, db)
    db.refresh(tool)
    return tool


@router.delete("/deletetoolimage/{tool_id}", status_code=200,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool_image(tool_id: int, db: Session = Depends(get_db)):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool.image_filename:
        path = UPLOAD_DIR / tool.image_filename
        if path.exists():
            path.unlink()
    crud.set_tool_image(db, tool, None)
    return {"message": f"Bild von Werkzeug '{tool.tool_name}' wurde gelöscht", "id": tool_id}
