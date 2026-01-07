from fastapi import APIRouter, HTTPException, Request

from Backend.API_Layer.utils.docusign_token_genearation_utils import generate_docusign_access_token
  
router = APIRouter()
@router.get("/docusign/token")
def get_docusign_token():
    """
    Generates a DocuSign JWT access token
    """
    try:

        print("Generating DocuSign access token...")
        token_data = generate_docusign_access_token()
        return {
            "access_token": token_data["access_token"],
            "expires_in": token_data["expires_in"],
            "token_type": token_data.get("token_type", "Bearer")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks/docusign")
async def docusign_webhook(request: Request):
    try:
        print("📩 Received DocuSign webhook")

        payload = await request.json()
        print("📦 Payload received:")
        print(payload)

        data = payload.get("data", {})
        envelope_id = data.get("envelopeId")

        envelope_summary = data.get("envelopeSummary", {})
        status = envelope_summary.get("status", "").lower()

        if not envelope_id or not status:
            print("⚠️ Missing envelopeId or status")
            return {"ok": True}

        if status == "completed":
            print(f"✅ Envelope completed: {envelope_id}")
            # update onboarding status
            # trigger next step

        elif status == "declined":
            print(f"❌ Envelope declined: {envelope_id}")
            # mark onboarding failed

        else:
            print(f"ℹ️ Ignored envelope status: {status}")

        return {"ok": True}

    except Exception as e:
        # IMPORTANT: never break DocuSign webhook
        print("🔥 Error processing DocuSign webhook")
        print("Error:", str(e))
        return {"ok": True}