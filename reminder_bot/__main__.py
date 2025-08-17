"""Module to start telegram-bot."""

import asyncio

from .run import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot exit")