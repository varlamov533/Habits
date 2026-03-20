import asyncio
from tables import metadata
from main import engine


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
    print("База готова!")