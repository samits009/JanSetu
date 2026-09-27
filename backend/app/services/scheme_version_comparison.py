"""
SchemeVersionComparisonService
================================
Deterministically compares two SchemeVersion objects for material policy changes.
Never uses LLM reasoning for the final material-change determination.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.models.scheme import SchemeVersion
from app.schemas.scheme import VersionFieldChange, SchemeVersionComparisonResponse


class SchemeVersionComparisonService:

    def compare(self, v_a: SchemeVersion, v_b: SchemeVersion) -> SchemeVersionComparisonResponse:
        changes: List[VersionFieldChange] = []

        # Compare eligibility rules
        rules_a = {r.rule_type: {"operator": r.operator, "value": r.value} for r in v_a.rules}
        rules_b = {r.rule_type: {"operator": r.operator, "value": r.value} for r in v_b.rules}

        all_rule_types = set(rules_a.keys()) | set(rules_b.keys())
        for rt in sorted(all_rule_types):
            old = rules_a.get(rt)
            new = rules_b.get(rt)
            if old != new:
                changes.append(VersionFieldChange(
                    field=f"rule:{rt}",
                    old_value=old,
                    new_value=new,
                    category="RULE"
                ))

        # Compare requirement definitions (stored as JSON snapshot)
        reqs_a = {r.get("name"): r for r in (v_a.requirement_definitions or [])}
        reqs_b = {r.get("name"): r for r in (v_b.requirement_definitions or [])}
        all_req_names = set(reqs_a.keys()) | set(reqs_b.keys())
        for name in sorted(all_req_names):
            old = reqs_a.get(name)
            new = reqs_b.get(name)
            if old != new:
                changes.append(VersionFieldChange(
                    field=f"requirement:{name}",
                    old_value=old,
                    new_value=new,
                    category="REQUIREMENT"
                ))

        # Compare benefits
        benefits_a = {b.benefit_type: {"amount": b.amount, "description": b.description} for b in v_a.benefits}
        benefits_b = {b.benefit_type: {"amount": b.amount, "description": b.description} for b in v_b.benefits}
        all_benefit_types = set(benefits_a.keys()) | set(benefits_b.keys())
        for bt in sorted(all_benefit_types):
            old = benefits_a.get(bt)
            new = benefits_b.get(bt)
            if old != new:
                changes.append(VersionFieldChange(
                    field=f"benefit:{bt}",
                    old_value=old,
                    new_value=new,
                    category="BENEFIT"
                ))

        # Compare portability rules
        portability_a = sorted([pr.portability_state for pr in v_a.portability_rules])
        portability_b = sorted([pr.portability_state for pr in v_b.portability_rules])
        if portability_a != portability_b:
            changes.append(VersionFieldChange(
                field="portability",
                old_value=portability_a,
                new_value=portability_b,
                category="PORTABILITY"
            ))

        # Compare renewal rules
        renewal_a = [{"required": rr.renewal_required, "days": rr.renewal_period_days} for rr in v_a.renewal_rules]
        renewal_b = [{"required": rr.renewal_required, "days": rr.renewal_period_days} for rr in v_b.renewal_rules]
        if renewal_a != renewal_b:
            changes.append(VersionFieldChange(
                field="renewal",
                old_value=renewal_a,
                new_value=renewal_b,
                category="RENEWAL"
            ))

        return SchemeVersionComparisonResponse(
            version_a_id=v_a.id,
            version_b_id=v_b.id,
            material_change=len(changes) > 0,
            changes=changes
        )
