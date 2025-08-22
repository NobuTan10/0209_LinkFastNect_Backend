import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker

# 環境変数の読み込み
base_path = Path(__file__).parents[1]  # backendディレクトリへのパスを想定
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# データベース接続情報（必須: 環境変数で設定）
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '3306')  # デフォルト3306
DB_NAME = os.getenv('DB_NAME')

# 早期チェック（起動時に不足があれば即時失敗させる）
_required = {"DB_USER": DB_USER, "DB_PASSWORD": DB_PASSWORD, "DB_HOST": DB_HOST, "DB_NAME": DB_NAME}
missing = [k for k, v in _required.items() if not v]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# SSL証明書のパス（DigiCert など）
ssl_cert = str(base_path / 'DigiCertGlobalRootCA.crt.pem')
if not Path(ssl_cert).exists():
    # 本番では App Service の /home/site/wwwroot 配下などに配置しておく
    raise RuntimeError(f"SSL CA cert not found at: {ssl_cert}")

# MySQLのURL構築（UTF-8を明示）
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

# SQLAlchemy Engine（Azure/MySQL向けの安定設定）
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {
            "ssl_ca": ssl_cert
        }
    },
    echo=False,           # 本番は False 推奨（必要なら環境変数で切替）
    pool_pre_ping=True,   # 接続生存確認
    pool_recycle=3600,    # MySQLのwait_timeout対策
    pool_size=5,
    max_overflow=10
)

# Baseクラス
Base = declarative_base()

# テーブル定義
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))

    def __repr__(self):
        return f"<Customer(customer_id='{self.customer_id}', name='{self.customer_name}')>"

# テーブル作成（初回のみ）
Base.metadata.create_all(engine)

# セッション
Session = sessionmaker(bind=engine)
session = Session()

from tabulate import tabulate
from sqlalchemy import text as sql_text

def add_test_data():
    try:
        with engine.begin() as conn:
            conn.execute(sql_text("DELETE FROM customers"))
        test_customers = [
            Customer(customer_id='C1111', customer_name='ああ',   age=6,  gender='男'),
            Customer(customer_id='C110',  customer_name='桃太郎', age=30, gender='女'),
        ]
        session.add_all(test_customers)
        session.commit()
        print("テストデータを追加しました")

        with engine.connect() as conn:
            print("\n=== customers テーブル ===")
            cols = conn.execute(sql_text("SHOW COLUMNS FROM customers")).fetchall()
            print(tabulate(cols, he
