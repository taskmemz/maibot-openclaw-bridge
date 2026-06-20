"""Backwards-compat entry point. Prefer using uvx:

    uvx --from git+https://github.com/taskmemz/maibot-openclaw-bridge maibot-openclaw-bridge

Or with pip:
    pip install -e . && maibot-openclaw-bridge
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from maibot_openclaw_bridge.__main__ import main

if __name__ == "__main__":
    asyncio.run(main())
