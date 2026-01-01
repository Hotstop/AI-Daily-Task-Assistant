"""
AI Task Assistant - Main Entry Point
====================================

By OkayYouGotMe

This is the heart of the application.
Initializes all components and starts the bot.

Simple to run:
    python main.py

That's it!
"""

import logging
import asyncio
import sys
from datetime import datetime

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_assistant.log')
    ]
)

logger = logging.getLogger(__name__)

# Now import everything else
from config.settings import (
    TELEGRAM_BOT_TOKEN, CLAUDE_API_KEY, DATABASE_URL,
    BRAND_NAME, BRAND_TAGLINE, validate_config
)
from database.operations import init_database
from bot.telegram_bot import TelegramBot


def print_banner():
    """Print startup banner"""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           {BRAND_NAME:^50s}           ║
║           {BRAND_TAGLINE:^50s}           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🤖 Telegram Bot: INITIALIZING...
🧠 Claude AI: CONNECTING...
💾 Database: CONNECTING...
⏰ Scheduler: PREPARING...

Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════════════════════
"""
    print(banner)


def check_configuration():
    """
    Verify all configuration is correct.
    
    Returns:
        True if valid, False otherwise
    """
    try:
        print("🔍 Validating configuration...")
        validate_config()
        print("✅ Configuration valid!\n")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}\n")
        print("Please check your .env file or environment variables!")
        return False


def initialize_database():
    """
    Initialize database and create tables.
    
    Returns:
        True if successful
    """
    try:
        print("💾 Initializing database...")
        init_database()
        print("✅ Database ready!\n")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}\n")
        print("Check your DATABASE_URL in .env file!")
        return False


async def main():
    """
    Main application entry point.
    
    Starts all components and runs the bot.
    """
    # Print banner
    print_banner()
    
    # Validate configuration
    if not check_configuration():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Create bot instance
    print("🤖 Starting Telegram bot...")
    bot = TelegramBot()
    
    print("✅ Telegram bot ready!\n")
    print("═══════════════════════════════════════════════════════════════")
    print("🚀 AI TASK ASSISTANT IS NOW RUNNING!")
    print("═══════════════════════════════════════════════════════════════\n")
    print("📱 Users can now message your bot on Telegram!")
    print("📊 Bot is listening for messages...")
    print("\n💡 Press Ctrl+C to stop the bot\n")
    
    logger.info("✅ Application started successfully")
    
    try:
        # Run bot (blocking)
        bot.run()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down gracefully...")
        logger.info("Application stopped by user")
    
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def run():
    """
    Simple runner function.
    
    Handles async event loop creation.
    """
    try:
        # For Python 3.11+, just run directly
        if sys.version_info >= (3, 11):
            asyncio.run(main())
        else:
            # For older Python, create event loop
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
    
    except KeyboardInterrupt:
        pass  # Handled in main()


if __name__ == "__main__":
    run()
