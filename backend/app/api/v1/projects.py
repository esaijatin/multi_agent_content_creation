import uuid

from fastapi import APIRouter, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession, OperatorUser
from app.models.database import Project
from app.models.schemas import ProjectCreate, ProjectResponse
from app.services.audit import write_audit_log

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    db: DbSession,
    current_user: OperatorUser,
) -> ProjectResponse:
    project = Project(
        name=body.name,
        description=body.description,
        owner_id=uuid.UUID(current_user.sub),
        metadata_=body.metadata,
    )
    db.add(project)
    await db.flush()

    await write_audit_log(
        db,
        actor_id=current_user.sub,
        action="project.create",
        resource_type="project",
        resource_id=str(project.id),
        details={"name": body.name},
    )

    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: DbSession, current_user: CurrentUser) -> list[ProjectResponse]:
    result = await db.execute(
        select(Project).where(Project.owner_id == uuid.UUID(current_user.sub))
    )
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectResponse:
    project = await db.get(Project, project_id)
    if not project or str(project.owner_id) != current_user.sub:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)
