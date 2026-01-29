#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Just A Rather Very Intelligent System
Main entry point
"""

import sys
from jarvis.assistant import main

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nЗавершение работы JARVIS...")
        print("До свидания, сэр.")
        sys.exit(0)
