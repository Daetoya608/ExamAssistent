import io

from fastapi import APIRouter, UploadFile, File, Depends

from app.api.dependencies import get_upload_document_use_case, get_mock_user
from app.domains.users.schemas import UserRead
from app.application.use_cases.upload_document import UploadDocumentUseCase

router = APIRouter()

@router.post("/files")
async def upload_document(
        file: UploadFile = File(...),
        current_user: UserRead = Depends(get_mock_user),
        use_case: UploadDocumentUseCase = Depends(get_upload_document_use_case)
):
    content = file.file.read()
    file_obj = io.BytesIO(content)

    result = use_case.execute(
        user_id=current_user.id,
        filename=file.filename,
        file_obj=file_obj,
    )

    if result:
        return {"status": "success", "user": current_user.username}
    else:
        return {"status": "error"}
