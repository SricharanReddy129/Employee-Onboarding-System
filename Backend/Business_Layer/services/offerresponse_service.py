from datetime import datetime
from ...API_Layer.interfaces.offerresponse_interface import PandaDocWebhookRequest, PandaDocWebhookResponse
from ...DAL.dao.offerresponse_dao import OfferResponseDAO


class OfferResponseService:

    @staticmethod
    async def process_pandadoc_webhook(payload: PandaDocWebhookRequest):
        """
        Business logic only:
        - Extract data from webhook
        - Validate event
        - Prepare update fields
        - Call DAO layer for DB operations
        """

        print("📌 Business Layer: Processing webhook")

        # ----------------------------
        # 1️⃣ Validate event
        # ----------------------------
        if payload.event != "document.completed":
            print("⚠ Ignoring webhook: Not a completed event.")
            return

        # ----------------------------
        # 2️⃣ Extract required fields
        # ----------------------------
        draft_id = payload.data.uuid                   # (pandadoc_draft_id stored in DB)
        pandadoc_signed_doc_id = payload.data.id       # (internal PandaDoc docId)
        signing_timestamp_raw = payload.date           # (ISO timestamp)
        document_status = payload.data.status          # should be "completed"

        print(f"➡ Draft UUID: {draft_id}")
        print(f"➡ Signed Doc ID: {pandadoc_signed_doc_id}")
        print(f"➡ Document Status: {document_status}")
        print(f"➡ Timestamp Raw: {signing_timestamp_raw}")

        # ----------------------------
        # 3️⃣ Convert timestamp
        # ----------------------------
        signing_timestamp = None
        if signing_timestamp_raw:
            try:
                signing_timestamp = datetime.fromisoformat(
                    signing_timestamp_raw.replace("Z", "+00:00")
                )
            except:
                signing_timestamp = datetime.utcnow()

        # ----------------------------
        # 4️⃣ Prepare values to update
        # ----------------------------
        update_data = {
            "draft_id": draft_id,
            "new_status": "Accepted",
            "signed_at": signing_timestamp,
            "signed_doc_id": pandadoc_signed_doc_id
        }

        print("📦 Prepared update data:", update_data)

        # ----------------------------
        # 5️⃣ Call DAO (No DB ops here)
        # ----------------------------
        await OfferResponseDAO.update_offer_from_webhook(update_data)

        print("✅ Passed update request to DAO layer")

        # ----------------------------
        # 6️⃣ Return webhook response
        # ----------------------------
        return PandaDocWebhookResponse(status="ok")