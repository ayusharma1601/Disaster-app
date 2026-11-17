from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

class RiskEngine:
    MAX_DATA_AGE_HOURS = 12.0  # FR-025: Observations older than 12h considered stale

    @staticmethod
    def evaluate_risk(observations: List[Dict], area_name: str = "Dhemaji District") -> Dict:
        if not observations:
            return {
                "area_name": area_name,
                "category": "DATA UNAVAILABLE",
                "score": None,
                "reasons": ["No telemetry observations available for this pilot area."],
                "limitations": "Risk cannot be inferred without sensor telemetry."
            }

        # Use UTC timestamp
        now = datetime.now(timezone.utc)
        valid_rainfall_values = []
        gauge_scores = []
        is_stale = False
        reasons = []

        for obs in observations:
            obs_time = obs.get("observed_at")
            if isinstance(obs_time, str):
                try:
                    obs_time = datetime.fromisoformat(obs_time)
                except ValueError:
                    try:
                        obs_time = datetime.strptime(obs_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        obs_time = now  # Fallback to current time if format is arbitrary

            # Harmonize timezone awareness to prevent runtime subtraction errors
            if obs_time is not None:
                if obs_time.tzinfo is None:
                    obs_time = obs_time.replace(tzinfo=timezone.utc)
                if (now - obs_time) > timedelta(hours=RiskEngine.MAX_DATA_AGE_HOURS):
                    is_stale = True

            val = obs.get("value")
            var = obs.get("variable")

            if var == "rainfall_24h" and val is not None:
                valid_rainfall_values.append(val)
            elif var == "water_level" and val is not None:
                warning_level = obs.get("warning_level") or 85.0
                danger_level = obs.get("danger_level") or 86.0
                if val >= danger_level:
                    gauge_scores.append(5.0)
                    reasons.append(f"River gauge at {obs.get('station_name', 'Station')} reached {val}m (at/above Danger Level {danger_level}m)")
                elif val >= warning_level:
                    gauge_scores.append(3.0)
                    reasons.append(f"River gauge at {obs.get('station_name', 'Station')} reached {val}m (approaching/at Warning Level {warning_level}m)")

        if is_stale:
            return {
                "area_name": area_name,
                "category": "STALE DATA / DATA UNAVAILABLE",
                "score": None,
                "reasons": ["Sensor observations are older than the maximum freshness window (12 hours)."],
                "limitations": "Do not assume low risk during sensor outages or communication latency."
            }

        # Rainfall scoring (FR-021)
        rain_score = 0.0
        if valid_rainfall_values:
            max_rain = max(valid_rainfall_values)
            if max_rain > 204.4:
                rain_score = 6.0
                reasons.append(f"Extremely Torrential rainfall recorded: {max_rain} mm in 24h")
            elif max_rain > 115.5:
                rain_score = 4.0
                reasons.append(f"Very Heavy rainfall recorded: {max_rain} mm in 24h")
            elif max_rain > 64.5:
                rain_score = 2.0
                reasons.append(f"Heavy rainfall recorded: {max_rain} mm in 24h")
            else:
                reasons.append(f"Rainfall within normal limits: max {max_rain} mm in 24h")

        max_gauge_score = max(gauge_scores) if gauge_scores else 0.0
        
        # Terrain multiplier for Dhemaji floodplains
        susceptibility_multiplier = 1.2
        composite_score = (rain_score + max_gauge_score) * susceptibility_multiplier

        # Category mapping
        if composite_score >= 6.0:
            category = "HIGH"
        elif composite_score >= 3.0:
            category = "MODERATE"
        else:
            category = "LOW"

        return {
            "area_name": area_name,
            "category": category,
            "score": round(composite_score, 2),
            "reasons": reasons,
            "assessed_at": now.isoformat(),
            "limitations": "Experimental rule-based decision support. Official ASDMA/CWC alerts take precedence."
        }
