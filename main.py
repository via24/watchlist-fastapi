import os
import uvicorn
from watchlist.main import app

if __name__ == "__main__":
    os.system("alembic upgrade head")
    """
    env: USERNAME, EMAIL, PWD, DB_URL, SECRET_KEY
    """
    uvicorn.run(app, host="0.0.0.0", port=80)
