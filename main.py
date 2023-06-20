import os
import uvicorn
from watchlist.main import app

if __name__ == "__main__":
    os.system("alembic upgrade head")
    """
    env: USERNAME, EMAIL, PWD, DB_URL, SECRET_KEY, HOST, PORT
    """
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", 8888)
    uvicorn.run(app, host=host, port=port)
