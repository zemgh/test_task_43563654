docker compose up --build  
docker exec wallets alembic upgrade head  
docker exec wallets python -m pytest -s tests.py  
