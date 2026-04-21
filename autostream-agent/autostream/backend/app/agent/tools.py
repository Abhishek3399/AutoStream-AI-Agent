import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mock lead-capture function (mirrors the assignment spec exactly)
# ---------------------------------------------------------------------------

def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Simulate persisting a qualified lead to a CRM / backend database.

    In production this would POST to Salesforce, HubSpot, or a
    custom webhook.  Here we simply log & print for demo purposes.

    Parameters
    ----------
    name     : Full name of the prospect
    email    : Contact email address
    platform : Creator platform (YouTube, Instagram, TikTok, etc.)

    Returns
    -------
    A human-readable confirmation string.
    """
    logger.info("mock_lead_capture called | name=%s email=%s platform=%s", name, email, platform)

    border = "=" * 56
    print(f"\n{border}")
    print("  ✅  LEAD CAPTURED SUCCESSFULLY")
    print(border)
    print(f"  Name     : {name}")
    print(f"  Email    : {email}")
    print(f"  Platform : {platform}")
    print(f"{border}\n")

    return (
        f"Lead successfully captured for {name} ({email}) "
        f"– creator on {platform}."
    )
