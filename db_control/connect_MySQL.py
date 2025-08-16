# db_control/connect_MySQL.py
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from urllib.parse import quote_plus
from pathlib import Path
from dotenv import load_dotenv
import os, re

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=ROOT / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")  # 文字列
RAW_DATABASE_URL = os.getenv("DATABASE_URL")  # あれば最優先だがバリデーション必須

def _is_valid_db_url(url: str) -> bool:
    if not url:
        return False
    # 文字列に 'None' が紛れていたら不正とみなす
    if re.search(r":None\b", url) or "None@" in url:
        return False
    return True

def build_url():
    # 1) DATABASE_URL が正しいときだけ使う
    if _is_valid_db_url(RAW_DATABASE_URL):
        return RAW_DATABASE_URL

    # 2) 個別変数から安全に構築（port は未指定なら None）
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise RuntimeError("DB 環境変数が不足しています（DB_USER/DB_PASSWORD/DB_HOST/DB_NAME）")

    port = int(DB_PORT) if (DB_PORT and DB_PORT.strip().isdigit()) else None

    return URL.create(
        drivername="mysql+pymysql",
        username=quote_plus(DB_USER),
        password=quote_plus(DB_PASSWORD),
        host=DB_HOST,
        port=port,
        database=DB_NAME,
    )

url = build_url()

# SSL を使う場合（Azure MySQL）
SSL_CERT_PATH = str(ROOT / "DigiCertGlobalRootCA.crt.pem")
use_ssl = os.getenv("DB_SSL", "true").lower() != "false"
connect_args = {"ssl": {"ca": SSL_CERT_PATH}} if use_ssl else {}

engine = create_engine(
    url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# デバッグ表示（安全）
print("Using DATABASE_URL?", _is_valid_db_url(RAW_DATABASE_URL))
print("DB_HOST =", DB_HOST, " DB_PORT =", repr(DB_PORT), " SSL cert exists? ->", os.path.exists(SSL_CERT_PATH))
