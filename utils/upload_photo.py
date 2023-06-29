from aiogram import types

from integrations.telegraph import FileUploader


async def photo_upload(m: types.Message, file_uploader: FileUploader):
    photo = m.photo[-1]
    uploaded_photo = await file_uploader.upload_photo(photo)

    return uploaded_photo.link
