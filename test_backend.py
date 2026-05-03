import asyncio
import httpx

async def test_login():
    async with httpx.AsyncClient() as client:
        # Test WRONG_PASSWORD
        res = await client.post("http://127.0.0.1:8000/api/auth/login", json={
            "rut": "22222222-2",
            "password": "wrong"
        })
        print("WRONG_PASSWORD:")
        print("Status:", res.status_code)
        print("Body:", res.text)

        # Test RUT_NOT_FOUND
        res = await client.post("http://127.0.0.1:8000/api/auth/login", json={
            "rut": "11111111-1",
            "password": "any"
        })
        print("\nRUT_NOT_FOUND:")
        print("Status:", res.status_code)
        print("Body:", res.text)

if __name__ == "__main__":
    asyncio.run(test_login())
