from typing import List, Dict, Any
from app.repositories.evidence import EvidenceRepository
from app.repositories.scheme import SchemeRepository

class EvidenceMatchingService:
    def __init__(self, evidence_repo: EvidenceRepository, scheme_repo: SchemeRepository):
        self.evidence_repo = evidence_repo
        self.scheme_repo = scheme_repo

    async def match(self, citizen_id: Any, scheme_id: Any) -> List[Dict[str, Any]]:
        scheme = await self.scheme_repo.get_with_rules(scheme_id)
        if not scheme:
            scheme = await self.scheme_repo.get_by_id(scheme_id)
        if not scheme:
            raise ValueError("Scheme not found")

        # Prioritize versioned requirements from current_version snapshot
        requirements = []
        if scheme.current_version and scheme.current_version.requirement_definitions:
            requirements = scheme.current_version.requirement_definitions
        elif scheme.requirement_definitions:
            requirements = scheme.requirement_definitions
        
        citizen_evidence = await self.evidence_repo.find_for_citizen(citizen_id)
        
        results = []
        for req in requirements:
            req_type = req.get("type")
            req_id = req.get("id", req_type)
            req_name = req.get("name", req_type)
            
            # Find matching evidence by type
            matching = [ev for ev in citizen_evidence if ev.evidence_type == req_type]
            
            if matching:
                # If we have evidence, check if document is verified
                verified = [ev for ev in matching if ev.document and ev.document.verification_status == "VERIFIED"]
                if verified:
                    results.append({
                        "requirement_id": req_id,
                        "requirement_name": req_name,
                        "requirement_type": req_type,
                        "status": "SATISFIED",
                        "evidence_ids": [str(ev.id) for ev in verified],
                        "document_ids": [str(ev.document.id) for ev in verified if ev.document],
                        "confidence": verified[0].confidence,
                        "reason": "Verified evidence found"
                    })
                else:
                    results.append({
                        "requirement_id": req_id,
                        "requirement_name": req_name,
                        "requirement_type": req_type,
                        "status": "UNCERTAIN",
                        "evidence_ids": [str(ev.id) for ev in matching],
                        "document_ids": [str(ev.document.id) for ev in matching if ev.document],
                        "confidence": matching[0].confidence,
                        "reason": "Evidence exists but is not fully verified"
                    })
            else:
                results.append({
                    "requirement_id": req_id,
                    "requirement_name": req_name,
                    "requirement_type": req_type,
                    "status": "MISSING",
                    "evidence_ids": [],
                    "document_ids": [],
                    "confidence": "NONE",
                    "reason": "No evidence matching requirement type"
                })

        return results

    async def evaluate_coverage(self, citizen_id: Any, scheme_id: Any) -> Dict[str, Any]:
        """
        Evaluates requirements coverage for benefit details.
        Returns a dict with 'requirements' and 'evidence_used'.
        """
        matches = await self.match(citizen_id, scheme_id)
        requirements_eval = []
        evidence_used = []
        seen_evidence_ids = set()

        citizen_evidence = await self.evidence_repo.find_for_citizen(citizen_id)
        ev_map = {str(ev.id): ev for ev in citizen_evidence}

        for m in matches:
            is_satisfied = (m["status"] == "SATISFIED")
            evidence_id = m["evidence_ids"][0] if (is_satisfied and m["evidence_ids"]) else None
            
            requirements_eval.append({
                "requirement_id": m["requirement_id"],
                "requirement_name": m["requirement_name"],
                "requirement_type": m["requirement_type"],
                "is_satisfied": is_satisfied,
                "evidence_id": evidence_id,
                "reason": m["reason"]
            })

            if evidence_id and evidence_id not in seen_evidence_ids:
                seen_evidence_ids.add(evidence_id)
                ev_obj = ev_map.get(evidence_id)
                if ev_obj:
                    doc_type = ev_obj.document.document_type if ev_obj.document else "UNKNOWN"
                    evidence_used.append({
                        "evidence_id": ev_obj.id,
                        "evidence_type": ev_obj.evidence_type,
                        "document_type": doc_type,
                        "confidence": ev_obj.confidence or "HIGH"
                    })

        return {
            "requirements": requirements_eval,
            "evidence_used": evidence_used
        }

