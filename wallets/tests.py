import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from models import Wallet


@pytest.mark.asyncio
async def test_routes():
    transport = ASGITransport(app=app)
    base_route = '/api/v1/wallets'

    def check_new_wallet(wallet: Wallet):
        assert len(wallet.__dict__) == 3
        assert wallet.balance == 0
        assert len(wallet.uuid) == 36
        assert type(wallet.uuid) == str

    async def check_deposit(wallet: Wallet):
        response = await client.post(f'{base_route}/{wallet.uuid}/operation',
                                     json={'operationType': 'DEPOSIT', 'amount': 100})
        assert response.status_code == 200

        response = await client.get(f'{base_route}/{wallet.uuid}')
        wallet = Wallet(**response.json())
        assert wallet.balance == 100

    async def check_withdraw(wallet: Wallet):
        response = await client.post(f'{base_route}/{wallet.uuid}/operation',
                                     json={'operationType': 'WITHDRAW', 'amount': 100})
        assert response.status_code == 200
        response = await client.get(f'{base_route}/{wallet.uuid}')
        wallet = Wallet(**response.json())
        assert wallet.balance == 0

    async def check_operation_json(wallet: Wallet):
        response = await client.post(f'{base_route}/{wallet.uuid}/operation',
                                     json={'operationType': 'TRANSFER', 'amount': 100})
        assert response.status_code == 400

        response = await client.post(f'{base_route}/{wallet.uuid}/operation',
                                     json={'operationType': 'DEPOSIT', 'amount': 100, 'test': 'test'})
        assert response.status_code == 422

        response = await client.post(f'{base_route}/{wallet.uuid}/operation',
                                     json={'operationType': 'DEPOSIT'})
        assert response.status_code == 422


    async with AsyncClient(transport=transport, base_url='http://localhost:8000') as client:
        response = await client.post(base_route + '/create')
        assert response.status_code == 201
        wallet = Wallet(**response.json())
        check_new_wallet(wallet)

        response = await client.get(f'{base_route}/{wallet.uuid}')
        assert response.status_code == 200

        response = await client.get(f'{base_route}/abracadabra')
        assert response.status_code == 404

        await check_deposit(wallet)
        await check_withdraw(wallet)
        await check_operation_json(wallet)

        response = await client.post(f'{base_route}/{wallet.uuid}/operation',
                                     json={'operationType': 'WITHDRAW', 'amount': 1000})
        assert response.status_code == 400
