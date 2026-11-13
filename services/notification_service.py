"""
Safe Notification Service with Local Logging Adapter
Implements notification abstractions without requiring live SMS or email credentials.
Guarantees never throwing uncaught exceptions if notification delivery fails.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("DisasterNotificationService")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[NOTIFICATION %(levelname)s] %(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class NotificationService:
    @staticmethod
    def send_alert(
        recipient: str,
        title: str,
        message: str,
        severity: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send emergency notification via local console logging adapter.
        Guaranteed to catch all internal exceptions and return delivery receipt.
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            log_line = (
                f"\n{'=' * 60}\n"
                f"🚨 EMERGENCY ALERT NOTIFICATION DISPATCHED\n"
                f"Recipient: {recipient}\n"
                f"Severity:  {severity.upper()}\n"
                f"Title:     {title}\n"
                f"Message:   {message}\n"
                f"Metadata:  {metadata or {}}\n"
                f"Timestamp: {timestamp}\n"
                f"{'=' * 60}"
            )
            logger.info(log_line)
            return {
                "status": "DELIVERED",
                "adapter": "console_local_adapter",
                "recipient": recipient,
                "severity": severity,
                "dispatched_at": timestamp
            }
        except Exception as e:
            # Never raise uncaught exception; log error gracefully
            logger.error(f"Notification delivery suppressed error: {e}")
            return {
                "status": "FAILED_GRACEFULLY",
                "error": str(e),
                "adapter": "console_local_adapter"
            }

    @staticmethod
    def notify_incident_update(incident_id: int, status: str, location: str, assigned_to: Optional[str] = None):
        """Dispatch incident status transition notification."""
        title = f"Incident #{incident_id} Transitioned to {status}"
        body = f"Incident at '{location}' is now {status}. Responder/Team: {assigned_to or 'Unassigned'}."
        return NotificationService.send_alert(
            recipient="SDRF_DHEMAJI_DISPATCH",
            title=title,
            message=body,
            severity="HIGH" if status in ["ASSIGNED", "IN PROGRESS"] else "INFO",
            metadata={"incident_id": incident_id, "status": status}
        )

    @staticmethod
    def notify_resource_allocation(resource_name: str, incident_id: int, responder: str):
        """Dispatch resource dispatch notification."""
        title = f"Resource Allocated: {resource_name}"
        body = f"Resource '{resource_name}' allocated to Incident #{incident_id} by Operator '{responder}'."
        return NotificationService.send_alert(
            recipient="DEOC_LOGISTICS_HQ",
            title=title,
            message=body,
            severity="CRITICAL",
            metadata={"resource_name": resource_name, "incident_id": incident_id}
        )
