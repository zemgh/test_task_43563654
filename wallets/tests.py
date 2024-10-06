import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from models import Wallet


@pytest.mark.asyncio
async def test_routes():
    transport = ASGITransport(app=app)
    base_route = 'http://localhost:8000/api/v1/wallets'

    async with AsyncClient(transport=transport, base_url=base_route) as client:
        """Создание кошелька"""
        wallet = await create_wallet(client)

        """Корректность атрибутов"""
        await check_wallets_details(wallet)

        """Получение кошелька по uuid"""
        await get_wallet(wallet.uuid, client)

        """Операций"""
        await check_deposit(wallet, client)
        await check_withdraw(wallet, client)
        await check_operation_json(wallet, client)

        """Проверка отрицательного баланса"""
        await check_negative_balance(wallet, client)


@pytest.mark.asyncio
async def create_wallet(client: AsyncClient) -> Wallet:
    response = await client.post('/create')
    assert response.status_code == 201, 'Объект не создан в БД'
    wallet = Wallet(**response.json())
    return wallet


@pytest.mark.asyncio
async def check_wallets_details(wallet: Wallet):
    """Корректность начальных атрибутов"""
    try:
        assert len(wallet.__dict__) == 3
        assert wallet.balance == 0
        assert len(wallet.uuid) == 36
        assert type(wallet.uuid) == str
    except AssertionError:
        raise AssertionError('Неверные стартовые атрибуты')


@pytest.mark.asyncio
async def get_wallet(uuid: str, client: AsyncClient):
    response = await client.get(f'/{uuid}')
    assert response.status_code == 200, 'Объект не найдет в БД'

    response = await client.get(f'/abracadabra')
    assert response.status_code == 404, 'Неверный статус код'


@pytest.mark.asyncio
async def check_deposit(wallet: Wallet, client: AsyncClient):
    """Проверка операций DEPOSIT"""

    response = await client.post(f'/{wallet.uuid}/operation',
                                 json={'operationType': 'DEPOSIT', 'amount': 100})
    assert response.status_code == 200, 'Операция DEPOSIT не выполнена'

    response = await client.get(f'/{wallet.uuid}')
    wallet = Wallet(**response.json())
    assert wallet.balance == 100, 'Баланс не изменился (DEPOSIT)'


@pytest.mark.asyncio
async def check_withdraw(wallet: Wallet, client: AsyncClient):
    """Проверка операций WITHDRAW"""

    response = await client.post(f'/{wallet.uuid}/operation',
                                 json={'operationType': 'WITHDRAW', 'amount': 100})
    assert response.status_code == 200, 'Операция WITHDRAW не выполнена'
    response = await client.get(f'/{wallet.uuid}')
    wallet = Wallet(**response.json())
    assert wallet.balance == 0, 'Баланс не изменился (WITHDRAW)'


@pytest.mark.asyncio
async def check_operation_json(wallet: Wallet, client: AsyncClient):
    """Валидация json"""

    """Некорректный тип операции"""
    response = await client.post(f'/{wallet.uuid}/operation',
                                 json={'operationType': "TRANSFER", 'amount': 100})
    assert response.status_code == 400, 'Неверный статус код/выполнена недопустимая операция'

    """Дополнительное поле"""
    response = await client.post(f'/{wallet.uuid}/operation',
                                 json={'operationType': 'DEPOSIT', 'amount': 100, "test": "test"})
    assert response.status_code == 422, 'Неверный статус код/неверное тело запроса прошло валидацию'

    """Недостающее поле"""
    response = await client.post(f'/{wallet.uuid}/operation',
                                 json={'operationType': 'DEPOSIT'})
    assert response.status_code == 422, 'Неверный статус код/неверное тело запроса прошло валидацию'


@pytest.mark.asyncio
async def check_negative_balance(wallet: Wallet, client: AsyncClient):
    response = await client.post(f'/{wallet.uuid}/operation',
                                 json={'operationType': 'WITHDRAW', 'amount': 1000})
    assert response.status_code == 400, 'Баланс не может быть отрицательным'
