"""
🚀 Reddit Newsletter Generator - Command Center
================================================
A beautiful CLI interface for generating your weekly AI newsletter.
"""

import time
import os
import sys
import argparse
from pathlib import Path

# Rich library for beautiful terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Install 'rich' for a better experience: pip install rich")

from src.config_loader import load_config, PROJECT_ROOT
from src.reddit_fetcher import fetch_posts
from src.llm_analyzer import generate_newsletter
from src.email_sender import send_email

# Initialize Rich console
console = Console() if RICH_AVAILABLE else None


def print_header():
    """Display the application header."""
    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold cyan]🚀 The Weekly Sync[/bold cyan]\n"
            "[dim]Your AI-Powered Reddit Newsletter Generator[/dim]",
            border_style="cyan"
        ))
    else:
        print("\n" + "="*50)
        print("🚀 The Weekly Sync")
        print("Your AI-Powered Reddit Newsletter Generator")
        print("="*50 + "\n")


def print_menu():
    """Display the interactive menu."""
    if RICH_AVAILABLE:
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="bold yellow")
        table.add_column("Description")
        table.add_row("[1]", "📧 Generate & Send Newsletter")
        table.add_row("[2]", "👀 Preview Only (No Email)")
        table.add_row("[3]", "⚙️  View Current Settings")
        table.add_row("[4]", "📂 Open Output Folder")
        table.add_row("[5]", "❌ Exit")
        console.print(table)
        console.print()
    else:
        print("[1] 📧 Generate & Send Newsletter")
        print("[2] 👀 Preview Only (No Email)")
        print("[3] ⚙️  View Current Settings")
        print("[4] 📂 Open Output Folder")
        print("[5] ❌ Exit")
        print()


def show_settings():
    """Display current configuration settings."""
    config = load_config()
    
    if RICH_AVAILABLE:
        # Subreddits table
        sub_table = Table(title="📡 Monitored Subreddits", show_header=False, border_style="blue")
        sub_table.add_column("Subreddit")
        for sub in config.get("subreddits", []):
            sub_table.add_row(f"r/{sub}")
        console.print(sub_table)
        console.print()
        
        # Fetch settings
        fetch = config.get("fetch", {})
        settings_table = Table(title="⚙️ Fetch Settings", border_style="green")
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Value", style="white")
        settings_table.add_row("Posts per subreddit", str(fetch.get("posts_per_subreddit", 5)))
        settings_table.add_row("Time period", fetch.get("time_period", "week"))
        settings_table.add_row("Delay between requests", f"{fetch.get('delay_between_requests', 1.0)}s")
        settings_table.add_row("Max retries", str(fetch.get("max_retries", 3)))
        console.print(settings_table)
        console.print()
        
        console.print("[dim]Edit config/settings.yaml to change these settings.[/dim]\n")
    else:
        print("\n--- Current Settings ---")
        print(f"Subreddits: {config.get('subreddits', [])}")
        print(f"Fetch settings: {config.get('fetch', {})}")
        print("Edit config/settings.yaml to change settings.\n")


def run_newsletter(send_email_flag=True):
    """
    Main newsletter generation logic.
    
    Args:
        send_email_flag: If True, send the email. If False, just generate.
    """
    config = load_config()
    subreddits = config.get("subreddits", [])
    fetch_settings = config.get("fetch", {})
    email_settings = config.get("email", {})
    newsletter_settings = config.get("newsletter", {})
    
    if RICH_AVAILABLE:
        console.print(f"\n[bold green]Starting newsletter generation for {len(subreddits)} subreddits...[/bold green]\n")
    else:
        print(f"\n🚀 Starting newsletter generation for {len(subreddits)} subreddits...\n")
    
    # 1. Fetch posts from all subreddits
    all_posts = []
    
    for sub in subreddits:
        if RICH_AVAILABLE:
            console.print(f"  📥 Fetching from [cyan]r/{sub}[/cyan]...")
        else:
            print(f"  📥 Fetching from r/{sub}...")
        
        posts = fetch_posts(
            sub, 
            limit=fetch_settings.get("posts_per_subreddit", 5),
            time_period=fetch_settings.get("time_period", "week")
        )
        
        # Tag posts with subreddit name
        for post in posts:
            post['title'] = f"[r/{sub}] {post['title']}"
        
        all_posts.extend(posts)
        time.sleep(fetch_settings.get("delay_between_requests", 1.0))
    
    if RICH_AVAILABLE:
        console.print(f"\n[bold]📦 Collected {len(all_posts)} posts total.[/bold]\n")
    else:
        print(f"\n📦 Collected {len(all_posts)} posts total.\n")
    
    if not all_posts:
        if RICH_AVAILABLE:
            console.print("[bold red]❌ No posts found. Check your internet connection or subreddit names.[/bold red]")
        else:
            print("❌ No posts found. Check your internet connection or subreddit names.")
        return False
    
    # 2. Generate newsletter with AI
    if RICH_AVAILABLE:
        console.print("👨‍🍳 Sending to Gemini for curation...")
    else:
        print("👨‍🍳 Sending to Gemini for curation...")
    
    result = generate_newsletter(all_posts)
    
    if not result:
        if RICH_AVAILABLE:
            console.print("[bold red]❌ Failed to generate newsletter.[/bold red]")
        else:
            print("❌ Failed to generate newsletter.")
        return False
    
    # 3. Save to file
    output_dir = newsletter_settings.get("output_directory", "output/newsletters")
    output_filename = newsletter_settings.get("output_filename", "weekly_digest.md")
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, output_filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(result['newsletter'])
    
    if RICH_AVAILABLE:
        console.print(f"\n[bold green]✅ Newsletter saved to:[/bold green] {filepath}")
    else:
        print(f"\n✅ Newsletter saved to: {filepath}")
    
    # 4. Send email (if enabled)
    if send_email_flag and email_settings.get("send_on_completion", True):
        if RICH_AVAILABLE:
            console.print("\n📧 Sending email...")
        else:
            print("\n📧 Sending email...")
        
        subject = email_settings.get("subject", "🚀 The Weekly Sync")
        send_email(result['newsletter'], subject=subject)
    elif not send_email_flag:
        if RICH_AVAILABLE:
            console.print("\n[dim]📧 Email skipped (preview mode).[/dim]")
        else:
            print("\n📧 Email skipped (preview mode).")
    
    return True


def open_output_folder():
    """Open the output folder in the system file explorer."""
    output_dir = PROJECT_ROOT / "output" / "newsletters"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if sys.platform == "win32":
        os.startfile(output_dir)
    elif sys.platform == "darwin":
        os.system(f'open "{output_dir}"')
    else:
        os.system(f'xdg-open "{output_dir}"')
    
    if RICH_AVAILABLE:
        console.print(f"[green]📂 Opened:[/green] {output_dir}")
    else:
        print(f"📂 Opened: {output_dir}")


def interactive_mode():
    """Run the interactive CLI menu."""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
        except KeyboardInterrupt:
            if RICH_AVAILABLE:
                console.print("\n[yellow]👋 Goodbye![/yellow]")
            else:
                print("\n👋 Goodbye!")
            break
        
        if choice == "1":
            run_newsletter(send_email_flag=True)
        elif choice == "2":
            run_newsletter(send_email_flag=False)
        elif choice == "3":
            show_settings()
        elif choice == "4":
            open_output_folder()
        elif choice == "5":
            if RICH_AVAILABLE:
                console.print("[yellow]👋 Goodbye![/yellow]")
            else:
                print("👋 Goodbye!")
            break
        else:
            if RICH_AVAILABLE:
                console.print("[red]Invalid choice. Please enter 1-5.[/red]")
            else:
                print("Invalid choice. Please enter 1-5.")
        
        print()  # Add spacing between actions


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="🚀 The Weekly Sync - AI-Powered Reddit Newsletter Generator"
    )
    parser.add_argument(
        "--auto", 
        action="store_true",
        help="Run automatically without interactive menu (for scheduled jobs)"
    )
    parser.add_argument(
        "--no-email",
        action="store_true", 
        help="Generate newsletter but don't send email"
    )
    
    args = parser.parse_args()
    
    if args.auto:
        # Non-interactive mode for GitHub Actions / cron jobs
        print("🤖 Running in automatic mode...")
        success = run_newsletter(send_email_flag=not args.no_email)
        sys.exit(0 if success else 1)
    else:
        # Interactive CLI mode
        interactive_mode()


if __name__ == "__main__":
    main()
