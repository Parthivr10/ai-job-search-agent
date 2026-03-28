from datetime import datetime, timezone


def time_ago(date_string):

    if not date_string:
        return "Unknown"

    try:
        job_date = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    except:
        return "Unknown"

    if job_date.tzinfo is None:
        job_date = job_date.replace(tzinfo=timezone.utc)

    now  = datetime.now(timezone.utc)
    diff = now - job_date

    days  = diff.days
    hours = diff.seconds // 3600

    if days > 0:
        return f"{days} days ago"

    if hours > 0:
        return f"{hours} hours ago"

    return "just now"
