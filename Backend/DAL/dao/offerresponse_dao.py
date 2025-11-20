from sqlalchemy import select
from ...DAL.models.models import OfferLetterDetails


class OfferResponseDAO:

    async def update_offer_from_webhook(self, update_data: dict):
        """
        Update offer letter fields when PandaDoc webhook notifies completion.
        """

        draft_id = update_data["draft_id"]
        new_status = update_data["new_status"]
        signed_at = update_data["signed_at"]
        signed_doc_id = update_data["signed_doc_id"]

        # 1. Fetch record by draft_id
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.pandadoc_draft_id == draft_id
            )
        )
        offer = result.scalar_one_or_none()

        if not offer:
            return None

        # 2. Update fields
        offer.status = new_status                     # "Accepted"
        offer.offer_signed_at = signed_at             # datetime
        offer.pandadoc_signed_doc_id = signed_doc_id  # internal PandaDoc doc-id

        # 3. Commit + refresh
        await self.db.commit()
        await self.db.refresh(offer)

        return offer
