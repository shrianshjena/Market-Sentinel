import asyncio
from main import app
from httpx import AsyncClient, ASGITransport

async def test_analyze():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        print("Fetching data for NALCO...")
        response = await ac.get("/api/analyze/NALCO")
        if response.status_code == 200:
            data = response.json()
            print("Status:", data["status"])
            print("Current Price:", data["data"]["current_price"])
            print("Data points (1-year):", len(data["data"]["historical_1y"]))
            print("Analysis Breakdown:")
            for k, v in data["data"]["analysis"].items():
                print(f"  {k}: {str(v).encode('ascii', 'ignore').decode('ascii')}")
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_analyze())
