from typing import List, Dict, Any
import datetime
from app.repositories.citizen import CitizenRepository
from app.repositories.scheme import BenefitRiskRepository
from app.models.application import BenefitRisk

class BenefitRiskService:
    def __init__(self, citizen_repo: CitizenRepository, risk_repo: BenefitRiskRepository):
        self.citizen_repo = citizen_repo
        self.risk_repo = risk_repo

    async def evaluate(self, citizen_id: Any) -> List[Dict[str, Any]]:
        citizen = await self.citizen_repo.get_full_welfare_context(citizen_id)
        if not citizen:
            raise ValueError("Citizen not found")

        risks = []
        today = datetime.date.today()

        for benefit in citizen.benefits:
            if benefit.status != "ACTIVE":
                continue

            if benefit.next_renewal_date and benefit.next_renewal_date < today + datetime.timedelta(days=30):
                risk = {
                    "benefit": benefit,
                    "risk_level": "HIGH" if benefit.next_renewal_date < today + datetime.timedelta(days=7) else "MEDIUM",
                    "reason": "Upcoming renewal deadline",
                    "deadline": benefit.next_renewal_date,
                    "recommended_action": "Submit renewal application"
                }
                risks.append(risk)
                
                existing_risks = [r for r in benefit.risks if r.risk_type == "RENEWAL" and not r.resolved_at]
                if not existing_risks:
                    await self.risk_repo.create(
                        benefit_id=benefit.id,
                        risk_type="RENEWAL",
                        description=risk["reason"],
                        severity=risk["risk_level"]
                    )
                    
        return risks
