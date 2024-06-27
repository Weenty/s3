import asyncio
from services.pgpool import run_migrate

loop = asyncio.get_event_loop()
loop.run_until_complete(run_migrate())