import asyncio

async def fetch_data():
    print("Start fetching data...")
    await asyncio.sleep(2)  # Simulate a network request
    print("Data fetched.")

async def process_data():
    print("Start processing data...")
    await asyncio.sleep(1)  # Simulate data processing
    print("Data processed.")

async def main():
    await asyncio.gather(fetch_data(), process_data())

asyncio.run(main())