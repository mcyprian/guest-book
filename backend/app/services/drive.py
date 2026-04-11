"""Google Drive upload service using a service account."""

import logging
from io import BytesIO

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_drive_service():
    """Build an authenticated Google Drive service client."""
    creds = Credentials.from_service_account_file(
        settings.google_service_account_key_path,
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=creds)


def upload_to_drive(file_buffer: BytesIO, filename: str, folder_id: str) -> str:
    """Upload a PDF file to Google Drive and return the web view link.

    Args:
        file_buffer: PDF content as BytesIO.
        filename: Name for the file in Drive.
        folder_id: Google Drive folder ID to upload into.

    Returns:
        Web view link URL for the uploaded file.
    """
    service = _get_drive_service()

    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    media = MediaIoBaseUpload(file_buffer, mimetype="application/pdf")

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id,webViewLink")
        .execute()
    )

    logger.info("Uploaded %s to Drive (id=%s)", filename, file["id"])
    return file.get("webViewLink", f"https://drive.google.com/file/d/{file['id']}")
