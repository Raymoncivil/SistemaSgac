import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Login to get token
        response = await client.post(
            "http://127.0.0.1:8000/api/auth/login",
            json={"rut": "13111222K", "password": "password123"}
        )
        print("Login:", response.status_code)
        token = response.json().get("access_token")
        
        # 2. Get activities
        response = await client.get(
            "http://127.0.0.1:8000/api/activities/",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("Get Activities:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    asyncio.run(main())
