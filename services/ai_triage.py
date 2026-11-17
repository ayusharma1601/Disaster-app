"""
AI Triage & Emergency Incident Intelligence Engine.
Performs zero-dependency NLP classification on community SOS incident reports.
Computes:
1. Incident category classification & urgency rating.
2. Threat/Severity Index score (0.00 to 1.00).
3. Recommended emergency resource allocation (Rescue Boat, SDRF Squad, Relief Camp, Medical Unit, etc.).
4. Actionable operational keywords and triage rationale.
"""

import math
import re
from typing import Dict, List, Optional

class IncidentTriageAI:
    """
    On-device NLP Triage classifier and priority assessment model.
    Runs locally with zero external network dependencies, ensuring resilience during total internet blackouts.
    """

    # Keyword lexicons with weighted severity impact
    CRITICAL_KEYWORDS = {
        "marooned": 0.95, "stranded": 0.90, "breach": 0.95, "breached": 0.95,
        "overtopping": 0.90, "drowning": 0.98, "submerged": 0.88, "trapped": 0.92,
        "swept away": 0.96, "collapse": 0.90, "collapsed": 0.90, "injured": 0.85,
        "casualty": 0.95, "children": 0.85, "infant": 0.90, "elderly": 0.85,
        "second floor": 0.88, "roof": 0.85, "rooftop": 0.88, "water rising fast": 0.92,
        "current strong": 0.85, "severe": 0.80, "dying": 0.98, "critical": 0.85
    }

    HIGH_KEYWORDS = {
        "waterlogging": 0.65, "flooded": 0.70, "inundated": 0.72, "cutoff": 0.75,
        "cut off": 0.75, "road blocked": 0.65, "culvert choked": 0.68, "erosion": 0.70,
        "embankment": 0.70, "danger level": 0.75, "no drinking water": 0.70,
        "food shortage": 0.68, "isolated": 0.72, "heavy rain": 0.60,
        "unwell": 0.75, "sick": 0.75, "fever": 0.70, "patient": 0.75, "stroke": 0.85,
        "heart attack": 0.90, "oxygen": 0.85, "dialysis": 0.85, "pregnant": 0.80
    }

    # Negation patterns to prevent false-positive critical alerts on safe conditions
    NEGATION_WORDS = {"not", "no", "never", "without", "safe", "cleared", "fine", "okay", "unharmed"}

    RESOURCE_MAPPING = [
        (["injured", "casualty", "medical", "fever", "sick", "unwell", "patient", "pregnant", "bleeding", "trauma", "doctor", "oxygen", "dialysis"], "Medical Unit"),
        (["boat", "marooned", "stranded", "trapped", "swept", "drowning", "roof", "rooftop", "river", "breach"], "Rescue Boat"),
        (["shelter", "homeless", "evacuation", "evacuate", "displaced", "relief camp", "houses flooded"], "Relief Camp"),
        (["drinking water", "water tanker", "dehydration", "thirst", "potable"], "Water Tanker"),
        (["embankment", "sandbags", "collapse", "siltation", "spillway", "culvert"], "SDRF Squad")
    ]

    @classmethod
    def _clean_text(cls, text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())

    @classmethod
    def _is_negated(cls, kw: str, text: str) -> bool:
        """
        Check if a keyword is preceded by negation or safe terms within 3 words
        (e.g., 'not stranded', 'everyone is safe', 'no breach', 'without injury').
        """
        pattern = rf"\b(not|no|never|without|safe|neither|cleared|fine|okay)\b(?:\s+\w+){{0,3}}\s+\b{re.escape(kw)}\b"
        return bool(re.search(pattern, text))

    @classmethod
    def triage_incident(cls, category: str, description: str, location_text: Optional[str] = None) -> Dict:
        """
        Analyzes incident text using rule-based keyword triage and negation-aware scoring to assign severity,
        triage urgency, resource recommendation, and operational guidance.
        """
        combined_text = cls._clean_text(f"{category} {description} {location_text or ''}")
        words = set(combined_text.split())

        # 1. Calculate Threat Index with Negation Awareness
        severity_hits = []
        negated_hits = []
        max_severity = 0.35  # baseline low/medium
        
        for kw, score in cls.CRITICAL_KEYWORDS.items():
            if kw in combined_text:
                if cls._is_negated(kw, combined_text):
                    negated_hits.append(kw)
                else:
                    severity_hits.append(kw)
                    if score > max_severity:
                        max_severity = score

        for kw, score in cls.HIGH_KEYWORDS.items():
            if kw in combined_text:
                if cls._is_negated(kw, combined_text):
                    negated_hits.append(kw)
                else:
                    severity_hits.append(kw)
                    if score > max_severity:
                        max_severity = score

        # If all risk keywords were explicitly negated, lower baseline to safe LOW
        if not severity_hits and negated_hits:
            max_severity = 0.20

        # Adjust score by word density
        density_bonus = min(0.15, len(severity_hits) * 0.04)
        calculated_severity = round(min(1.0, max_severity + density_bonus), 2)

        # 2. Determine Urgency Tier
        if calculated_severity >= 0.85:
            urgency_tier = "CRITICAL"
        elif calculated_severity >= 0.65:
            urgency_tier = "HIGH"
        elif calculated_severity >= 0.45:
            urgency_tier = "MEDIUM"
        else:
            urgency_tier = "LOW"

        # 3. Recommend Matching Resource
        recommended_resource = "SDRF Squad"  # default general response
        for triggers, res_name in cls.RESOURCE_MAPPING:
            # Check triggers that are not negated
            active_triggers = [t for t in triggers if t in combined_text and not cls._is_negated(t, combined_text)]
            if active_triggers:
                recommended_resource = res_name
                break

        # 4. Generate Operational Triage Summary
        rationale = []
        if severity_hits:
            rationale.append(f"Identified priority indicators: {', '.join(severity_hits[:4])}.")
        if negated_hits:
            rationale.append(f"Detected safe/negated context for: {', '.join(negated_hits[:3])}.")
        if "breach" in words or "breached" in words:
            if not cls._is_negated("breach", combined_text) and not cls._is_negated("breached", combined_text):
                rationale.append("Structural risk detected: Immediate embankment alert dispatch required.")
        if "stranded" in words or "marooned" in words:
            if not cls._is_negated("stranded", combined_text) and not cls._is_negated("marooned", combined_text):
                rationale.append("Human life at imminent risk: Prioritize watercraft search & rescue.")

        if not rationale:
            rationale.append("Standard priority report; routine field verification recommended.")

        return {
            "ai_severity_score": calculated_severity,
            "ai_suggested_urgency": urgency_tier,
            "ai_recommended_resource": recommended_resource,
            "detected_risk_indicators": severity_hits,
            "negated_risk_indicators": negated_hits,
            "triage_rationale": " ".join(rationale),
            "model_version": "Rule-Based Keyword Triage (Offline Explainable)"
        }
