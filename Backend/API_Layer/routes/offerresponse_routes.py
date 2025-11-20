from fastapi import APIRouter, Request, HTTPException
from ...API_Layer.interfaces.offerresponse_interface import (
    PandaDocWebhookRequest, 
    PandaDocWebhookResponse
)
from ...Business_Layer.services.offerresponse_service import OfferResponseService

router = APIRouter()

@router.post("/offerletter-accepted", response_model=PandaDocWebhookResponse)
async def offerletter_accepted_webhook(request: Request):
    """
    Receives PandaDoc webhook when candidate signs the offer letter.
    """

    try:
        # 1. Parse incoming webhook JSON
        payload_json = await request.json()
        print("📩 Incoming PandaDoc Webhook Payload:", payload_json)

        # 2. Validate using Interface Layer (Pydantic)
        payload = PandaDocWebhookRequest(**payload_json)

        # 3. Call Business Layer to process the webhook
        await OfferResponseService.process_pandadoc_webhook(payload)

        # 4. Return required success response to PandaDoc
        return PandaDocWebhookResponse(status="ok")

    except Exception as e:
        print("❌ Error processing webhook:", str(e))
        # Still return 200 OK so PandaDoc doesn't retry
        return PandaDocWebhookResponse(status="ok")