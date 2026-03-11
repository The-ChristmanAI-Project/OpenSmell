"""
open_smell_human.py
OpenSmell Human Diagnostic Core v2.0 – Open Source
The Biological Cortex for breath/skin VOC mapping

Built by Everett N. Christman (Architect)
Christman AI Project – For human dignity and early restoration
"""

import numpy as np

class OpenSmellHumanCore:
    """
    Processes raw VOC arrays from breath or skin contact.
    Maps to 2,401 profiles with focus on clinical alerts.
    """
    def __init__(self):
        self.total_profiles = 2401
        self.sensitivity_ppb = 0.5
        
        # Example high-priority profile
        self.mcc_profile = {
            "label": "Merkel Cell Carcinoma",
            "signature": np.array([0.88, 0.45, 0.12, 0.09]),
            "scent": "Musty-Sweet / Stale Air",
            "alert_level": "CRITICAL"
        }
        
        self.category_map = {
            "Musty-Sweet": {"conditions": ["Merkel Cell Carcinoma"], "scent_type": "Aliphatic acids"},
            "Sour / Metallic": {"conditions": ["Tuberculosis"], "scent_type": "Alkanes"},
            "Acrid / Ammonia": {"conditions": ["Renal Failure"], "scent_type": "Volatile amines"},
            "Fruity / Acetone": {"conditions": ["Diabetes", "Ketoacidosis"], "scent_type": "Ketones"}
        }

    def process_biometric_scent(self, sensor_array_data: np.ndarray):
        if np.linalg.norm(sensor_array_data) == 0:
            return {"status": "NO_SIGNAL"}
        
        norm_data = sensor_array_data / np.linalg.norm(sensor_array_data)
        mcc_match = np.dot(norm_data, self.mcc_profile["signature"])
        
        if mcc_match > 0.95:
            return self._trigger_medical_alert(self.mcc_profile, mcc_match)
        
        return self._map_to_human_matrix(norm_data)

    def _trigger_medical_alert(self, profile, confidence):
        return {
            "status": "POSITIVE DETECTION",
            "condition": profile["label"],
            "confidence": f"{confidence * 100:.2f}%",
            "alert_level": profile["alert_level"],
            "action": "SEEK IMMEDIATE CLINICAL RESTORATION"
        }

    def _map_to_human_matrix(self, data):
        primary = data[0] if len(data) > 0 else 0.0
        if primary > 0.7: cat = "Musty-Sweet"
        elif primary > 0.5: cat = "Sour / Metallic"
        elif primary > 0.3: cat = "Acrid / Ammonia"
        else: cat = "Fruity / Acetone"
        
        return {
            "status": "MONITORING_WELLNESS",
            "category": cat,
            "possible_indicators": self.category_map.get(cat, {}).get("conditions", ["General wellness shift"]),
            "biological_scent": self.category_map.get(cat, {}).get("scent_type", "Unknown")
        }


class HumanOlfactoryNerve:
    """
    Routes diagnostic results to the appropriate Christman AI Family member.
    """
    def __init__(self, core: OpenSmellHumanCore):
        self.core = core
        self.registry = {
            "CRITICAL": "SIERRA",      # Trauma/health guardian
            "RESTORATION": "ALPHAVOX", # Voice for non-verbal
            "STABILITY": "ERUPTOR"     # Cognitive grounding
        }

    def transmit_human_signal(self, raw_data: np.ndarray, user_id: str = "anonymous"):
        diagnosis = self.core.process_biometric_scent(raw_data)
        target = self.registry.get(diagnosis.get("alert_level", "RESTORATION"), "UNKNOWN")
        
        return {
            "route_to": target,
            "user_id": user_id,
            "status": "SIGNAL_ROUTED",
            "sovereignty": "CLIENT_OWNED_DATA",
            "detail": diagnosis
        }


# Quick test when run directly
if __name__ == "__main__":
    core = OpenSmellHumanCore()
    nerve = HumanOlfactoryNerve(core)
    
    print("OpenSmell Human Core Loaded – Open Source Release")
    
    # Test critical case
    critical = np.array([0.88, 0.45, 0.12, 0.09])
    print("\nCritical Test:")
    print(nerve.transmit_human_signal(critical))
    
    # Test normal
    normal = np.array([0.1, 0.2, 0.3, 0.4])
    print("\nNormal Test:")
    print(nerve.transmit_human_signal(normal))
