from sqlalchemy import select
from ...DAL.models.models import OfferLetterDetails


class OfferResponseDAO:

    async def update_offer_from_webhook(self, update_data: dict):
        """
        Update offer letter fields when PandaDoc webhook notifies completion.
        """

        doc_id = update_data["doc_id"]
        new_status = update_data["new_status"]
        signed_at = update_data["offer_signed_at"]

        # 1. Fetch record by doc_id (stored in pandadoc_draft_id)
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.pandadoc_draft_id == doc_id
            )
        )
        offer = result.scalar_one_or_none()

        if not offer:
            return None

        # 2. Update fields
        offer.status = new_status            # "Accepted"
        offer.offer_signed_at = signed_at    # datetime from webhook

        # 3. Commit + refresh
        await self.db.commit()
        await self.db.refresh(offer)

        return offer
