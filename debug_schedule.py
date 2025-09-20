#!/usr/bin/env python3
"""
GitHub Actions Schedule Debug Script

This script helps debug why GitHub Actions might not be running on schedule.
It checks the current state and predicts when the next run should occur.
"""

import json
from datetime import datetime, timedelta


def analyze_github_actions_schedule():
    """Analyze GitHub Actions schedule and current state"""
    print("🔍 GitHub Actions Schedule Analysis")
    print("=" * 50)
    
    # Load current state
    try:
        with open('posted_articles.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ No posted_articles.json found")
        return
    
    last_run_str = data.get('last_run_time')
    queued_count = len(data.get('queued_articles', []))
    posted_count = len(data.get('posted_uris', []))
    
    print(f"📊 Current State:")
    print(f"   - Last run: {last_run_str}")
    print(f"   - Posted articles: {posted_count}")
    print(f"   - Queued articles: {queued_count}")
    
    if not last_run_str:
        print("⚠️  No last run time found")
        return
    
    # Parse last run time
    try:
        last_run = datetime.fromisoformat(last_run_str)
    except ValueError:
        print("❌ Invalid last run time format")
        return
    
    now = datetime.now()
    minutes_since_last = (now - last_run).total_seconds() / 60
    
    print(f"⏰ Timing Analysis:")
    print(f"   - Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - Minutes since last run: {minutes_since_last:.1f}")
    
    # GitHub Actions schedule
    schedule = []
    for h in [0, 3, 6, 9, 12, 15, 18, 21]:
        schedule.append((h, 0))
    for h in [1, 4, 7, 10, 13, 16, 19, 22]:
        schedule.append((h, 30))
    schedule.sort()
    
    # Find next scheduled time
    current_time_in_minutes = now.hour * 60 + now.minute
    next_run_found = False
    
    for hour, minute in schedule:
        scheduled_time = hour * 60 + minute
        if scheduled_time > current_time_in_minutes:
            next_hour, next_minute = hour, minute
            minutes_until_next = scheduled_time - current_time_in_minutes
            next_run_found = True
            break
    
    if not next_run_found:
        # Next run is tomorrow at 00:00
        next_hour, next_minute = 0, 0
        minutes_until_next = (24 * 60) - current_time_in_minutes
    
    print(f"📅 Schedule Analysis:")
    print(f"   - Next scheduled run: {next_hour:02d}:{next_minute:02d}")
    print(f"   - Minutes until next run: {minutes_until_next}")
    
    # Determine if bot should have run by now
    should_run = minutes_since_last >= 90
    print(f"🎯 Decision Analysis:")
    print(f"   - Should run now? {'YES' if should_run else 'NO'} (90-minute rule)")
    print(f"   - Minimum interval met? {'YES' if minutes_since_last >= 90 else f'NO ({90 - minutes_since_last:.1f} minutes remaining)'}")
    
    # Check for potential issues
    print(f"🚨 Potential Issues:")
    
    if queued_count > 0 and should_run:
        print(f"   - ⚠️  {queued_count} articles queued but not posted for {minutes_since_last:.1f} minutes")
        print("   - Possible causes:")
        print("     • GitHub Actions not triggering on schedule") 
        print("     • Missing repository secrets (API keys)")
        print("     • Workflow execution failures")
        print("     • Rate limiting preventing execution")
    elif queued_count > 0:
        print(f"   - ℹ️  {queued_count} articles queued, waiting for next schedule")
    else:
        print("   - ✅ No queued articles")
    
    if minutes_since_last > 180:  # More than 3 hours
        print(f"   - ⚠️  Very long time since last run ({minutes_since_last/60:.1f} hours)")
        print("   - This suggests GitHub Actions may not be working")
    
    # Check rate limiting
    try:
        with open('rate_limit_cooldown.json', 'r') as f:
            cooldown_data = json.load(f)
            cooldown_until = datetime.fromisoformat(cooldown_data['cooldown_until'])
            if cooldown_until > now:
                remaining = (cooldown_until - now).total_seconds() / 60
                print(f"   - 🔒 Rate limit cooldown active: {remaining:.1f} minutes remaining")
            else:
                print(f"   - ⚠️  Old rate limit file found (should be cleaned up)")
    except FileNotFoundError:
        print("   - ✅ No rate limit cooldown active")
    
    print("\n" + "=" * 50)
    print("💡 Recommendations:")
    
    if queued_count > 0 and should_run:
        print("   1. Check GitHub Actions workflow runs in repository")
        print("   2. Verify repository secrets are configured")
        print("   3. Check workflow execution logs for errors")
        print("   4. Consider manual workflow dispatch to test")
    elif queued_count == 0:
        print("   1. System appears to be working normally")
        print("   2. No immediate action needed")
    else:
        print("   1. Wait for next scheduled run")
        print("   2. Monitor for successful execution")


if __name__ == "__main__":
    analyze_github_actions_schedule()