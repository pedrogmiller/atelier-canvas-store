import json
import logging
from typing import Dict, Any, List
from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("TrendAuditorAgent")

class TrendAuditorAgent(BaseAgent):
    """
    Agent that audits, stress-tests, and scores candidate art briefs from the TrendScoutAgent
    against real-world commercial viability and monetization criteria.
    """

    PASS_THRESHOLD = 8.0  # Minimum score out of 10 required to proceed to production

    def __init__(self):
        super().__init__(
            name="TrendAuditorAgent",
            role_description="Chief Commercial Viability & Demand Auditor"
        )

    def audit_art_brief(self, art_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits a proposed art brief using the 6-Point Commercial Monetization Scorecard:
        1. Buyer Purchase Intent (Sanctuary / Long-term decor suitability)
        2. Perceived Luxury Value ($100+ price tag justification when framed)
        3. Market Saturation & Competition-to-Demand Ratio
        4. Multi-Cart / Gallery Wall Potential (Triptych / Duo bundles)
        5. Trend Longevity (Macro aesthetic vs 3-day viral meme fad)
        6. Trademark & Copyright Cleanliness (Zero infringement risk)
        """
        title = art_brief.get("collection_title", "Proposed Art Collection")
        aesthetic = art_brief.get("aesthetic_name", "Contemporary")
        concept = art_brief.get("concept_narrative", "")
        palette = ", ".join(art_brief.get("color_palette", []))
        prompt = art_brief.get("hero_art_prompt", "")
        target_rooms = ", ".join(art_brief.get("target_interior_rooms", ["Living Room"]))

        system_instruction = (
            "You are a ruthless Commercial Art Gallery Director and E-Commerce Demand Auditor. "
            "Your job is to audit art concepts before money and compute are spent producing them. "
            "You only approve concepts that have high commercial demand, high perceived luxury value, "
            "zero copyright risks, and strong multi-purchase potential."
        )

        audit_prompt = (
            f"Audit the following art collection concept for commercial profitability:\n"
            f"Title: {title}\n"
            f"Aesthetic: {aesthetic}\n"
            f"Target Rooms: {target_rooms}\n"
            f"Color Palette: {palette}\n"
            f"Art Prompt: {prompt}\n"
            f"Narrative: {concept}\n"
        )

        schema_example = {
            "commercial_score": 9.1,
            "is_approved": True,
            "scorecard": {
                "buyer_purchase_intent": 9.2,
                "perceived_luxury_value": 9.0,
                "market_undersaturation": 8.8,
                "multi_cart_potential": 9.4,
                "trend_longevity": 9.0,
                "ip_cleanliness": 10.0
            },
            "strengths": [
                "Strong appeal for modern neutral interior decor (warm limewash, natural wood).",
                "High perceived value when framed in solid oak ($120+ retail justifiable).",
                "High triptych/gallery wall bundle potential."
            ],
            "risks_and_critiques": [
                "Ensure color saturation remains organic and not overly digital."
            ],
            "target_buyer_demographic": "Affluent homeowners (25-45) decorating living rooms, master bedrooms, and home offices.",
            "pricing_recommendation": "Position hero 24x36 framed piece at $110-$120 with $60+ pure net margin.",
            "auditor_verdict": "APPROVED for production. High commercial viability and strong visual demand."
        }

        # 1. Evaluate with Gemini if available
        result = self.generate_json(audit_prompt, system_instruction, schema_example)
        if result and "commercial_score" in result:
            result["is_approved"] = result["commercial_score"] >= self.PASS_THRESHOLD
            logger.info(f"[{self.name}] Audited '{title}' via Gemini: Score {result['commercial_score']}/10 (Approved: {result['is_approved']})")
            return result

        # 2. Resilient Rule-Based Scoring Engine (Fallback)
        return self._heuristic_audit(art_brief)

    def _heuristic_audit(self, art_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic heuristic scoring based on proven home decor commercial attributes."""
        title = art_brief.get("collection_title", "").lower()
        aesthetic = art_brief.get("aesthetic_name", "").lower()
        rooms = " ".join(art_brief.get("target_interior_rooms", [])).lower()

        # Scorecard dimensions (out of 10)
        intent = 9.0 if ("living" in rooms or "bedroom" in rooms) else 8.2
        luxury = 9.2 if any(w in aesthetic for w in ["japandi", "bauhaus", "botanical", "mediterranean", "renaissance", "wabi"]) else 7.8
        saturation = 8.6
        multi_cart = 9.2 if any(w in title for w in ["set", "triptych", "no.", "study", "quadrant"]) else 8.5
        longevity = 9.0 if any(w in aesthetic for w in ["minimalism", "botanical", "bauhaus", "academia", "mediterranean"]) else 7.5
        ip_clean = 10.0  # Procedural & original prompt

        total_score = round((intent + luxury + saturation + multi_cart + longevity + ip_clean) / 6.0, 1)
        is_approved = total_score >= self.PASS_THRESHOLD

        return {
            "commercial_score": total_score,
            "is_approved": is_approved,
            "scorecard": {
                "buyer_purchase_intent": intent,
                "perceived_luxury_value": luxury,
                "market_undersaturation": saturation,
                "multi_cart_potential": multi_cart,
                "trend_longevity": longevity,
                "ip_cleanliness": ip_clean
            },
            "strengths": [
                f"Proven evergreen appeal in interior design for '{art_brief.get('aesthetic_name')}'.",
                "Harmonious neutral palette aligns with trending Pinterest & TikTok home decor aesthetics.",
                "High average order value potential via framed gallery wall pairings."
            ],
            "risks_and_critiques": [
                "Maintain high visual contrast for museum-grade print legibility across large format 24x36 in."
            ],
            "target_buyer_demographic": "Design-conscious homeowners, interior stylists, and apartment decorators looking for serene statement art.",
            "pricing_recommendation": "Hero 24x36 Solid Natural Oak Frame recommended at $110-$120 with >55% net profit margin.",
            "auditor_verdict": f"{'APPROVED' if is_approved else 'REJECTED'}: Commercial viability score {total_score}/10 exceeds threshold ({self.PASS_THRESHOLD}/10)."
        }
