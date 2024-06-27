from fastapi import APIRouter, UploadFile, File, HTTPException
from worker import resize_image_and_upload
from services.images import insert_file, get_files
import json
router = APIRouter()

@router.post('/')
async def send_images(file: UploadFile = File(...)):
    if len(file.filename) > 100:
        raise HTTPException(400, 'too long filename')
    fileId = await insert_file('')
    bytes = await file.read()
    resize_image_and_upload.delay(fileId, bytes, file.filename)
    return {'fileId': fileId}

@router.get('/{page}')
async def get_images(page: int):
    return await get_files(page)