# Process attachments in the message.
import aiohttp
import fitz  # PyMuPDF
from loguru import logger


async def process_attachments(attachment):
    attachment_name = attachment.filename
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            if resp.status != 200:
                raise Exception("HTTP Error: Unable to get file")
            # Check if the attachment is an image
            if any(
                attachment_name.lower().endswith(ext)
                for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
            ):
                logger.info("🖼️ Processing Image")
                image_data = await process_image(attachment)
                return {"mime_type": "image/jpeg", "data": image_data}
            # Check if the attachment is a PDF
            elif attachment_name.lower().endswith(".pdf"):
                logger.info("📄 Processing PDF")
                pdf_data = await resp.read()
                file_data = await process_pdf(pdf_data)
                response_text = f"{attachment_name}: {file_data}"
                logger.debug(response_text)
                return response_text
            else:
                logger.info("📄 Processing Other Attachments")
                file_data = await resp.text()
                response_text = f"{attachment_name}: {file_data}"
                logger.debug(response_text)
                return response_text


async def process_pdf(pdf_data):
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()
    pdf_document.close()
    text = " ".join(text.split()).strip()
    return text


async def process_image(attachment):
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            if resp.status != 200:
                return None
            return await resp.read()
