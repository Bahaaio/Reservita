import io

import qrcode
from fastapi.responses import StreamingResponse
from app.core.config import settings


def generate_qr_code(
    data: str,
) -> io.BytesIO:
    """
    Generate a QR code image and return as BytesIO buffer.

    Args:
        data: The data to encode in the QR code
        box_size: Size of each box in pixels
        border: Border size in boxes

    Returns:
        BytesIO buffer containing the QR code PNG image
    """
    qr = qrcode.QRCode(
        box_size=settings.QR_CODE_BOX_SIZE,
        border=settings.QR_CODE_BORDER_SIZE,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()

    img.save(buf)
    buf.seek(0)

    return buf


def qr_code_response(
    qr_buffer: io.BytesIO,
    filename: str = "qr.png",
) -> StreamingResponse:
    """
    Create a StreamingResponse from a QR code buffer.

    Args:
        qr_buffer: BytesIO buffer containing the QR code image
        filename: The filename for the Content-Disposition header

    Returns:
        StreamingResponse for the QR code PNG image
    """
    return StreamingResponse(
        qr_buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )
