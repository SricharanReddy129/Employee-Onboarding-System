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

    print("📬 API Layer: Received PandaDoc webhook for offer letter acceptance")

    try:
        payload_json = await request.json()
        print("📩 Incoming PandaDoc Webhook Payload:", payload_json)

        # If PandaDoc sends a list → iterate through them
        if isinstance(payload_json, list):
            payloads = payload_json
        else:
            payloads = [payload_json]

        responses = []
        for p in payloads:
            try:
                payload = PandaDocWebhookRequest(**p)
                response = await OfferResponseService.process_pandadoc_webhook(payload)
                responses.append(response)
            except Exception as e:
                print("❌ Error processing single webhook entry:", e)

        # Always return OK
        return PandaDocWebhookResponse(status="ok")


    except Exception as e:
        print("❌ Error processing webhook:", str(e))
        # Still return 200 OK so PandaDoc doesn't retry
        return PandaDocWebhookResponse(status="error")