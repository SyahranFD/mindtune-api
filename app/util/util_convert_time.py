from datetime import datetime, timedelta


def calculate_time_ago(created_at):
    """Convert created_at to a human-readable time ago format"""
    try:
        now = datetime.now()
        diff = now - created_at

        if diff < timedelta(minutes=1):
            return "just now"

        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minutes ago"

        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hours ago"

        elif diff < timedelta(weeks=1):
            days = diff.days
            return f"{days} days ago"

        elif diff < timedelta(days=30):
            weeks = int(diff.days / 7)
            return f"{weeks} weeks ago"

        elif diff < timedelta(days=365):
            months = int(diff.days / 30)
            return f"{months} months ago"

        else:
            years = int(diff.days / 365)
            return f"{years} years ago"

    except Exception:
        return "unknown time"