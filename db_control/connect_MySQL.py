from sqlalchemy import create_engine
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
base_path = Path(__file__).parents[1]
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '3306')  # 念のためデフォルト
DB_NAME = os.getenv('DB_NAME')

# 早期バリデーション（どれか欠けたら即エラー）
missing = [k for k, v in {
    "DB_USER": DB_USER, "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST, "DB_PORT": DB_PORT, "DB_NAME": DB_NAME
}.items() if not v]
if missing:
    raise RuntimeError(f".env の設定不足: {', '.join(missing)}  (場所: {env_path})")

# SSL証明書のパス
ssl_cert = str(base_path / 'DigiCertGlobalRootCA.crt.pem')
if not os.path.exists(ssl_cert):
    raise FileNotFoundError(f"SSL証明書が見つかりません: {ssl_cert}")

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 見やすい確認ログ（パスワードは伏せる）
print(f"[DB] host={DB_HOST} port={DB_PORT} db={DB_NAME} user={DB_USER}")
print(f"[DB] ssl_ca exists: {os.path.exists(ssl_cert)} -> {ssl_cert}")
print(f"[ENV] loaded from: {env_path}")

# エンジンの作成（SSL設定を追加）
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {"ssl_ca": ssl_cert}},
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)


print("Current working directory:", os.getcwd())
print("Certificate file exists:", os.path.exists('DigiCertGlobalRootCA.crt.pem'))

# from sqlalchemy import create_engine
# import os
# from pathlib import Path
# from dotenv import load_dotenv

# # 環境変数の読み込み
# base_path = Path(__file__).parents[1]  # backendディレクトリへのパス
# # env_path = base_path / '.env'
# # load_dotenv(dotenv_path=env_path)

# # データベース接続情報
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_HOST = os.getenv('DB_HOST')
# DB_PORT = os.getenv('DB_PORT')
# DB_NAME = os.getenv('DB_NAME')

# # SSL証明書のパス
# ssl_cert = str(base_path / 'DigiCertGlobalRootCA.crt.pem')

# # MySQLのURL構築
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# # エンジンの作成（SSL設定を追加）
# engine = create_engine(
#     DATABASE_URL,
#     connect_args={
#         "ssl": {
#             "ssl_ca": ssl_cert
#         }
#     },
#     echo=True,
#     pool_pre_ping=True,
#     pool_recycle=3600
# )

# from sqlalchemy import create_engine

# import os
# from dotenv import load_dotenv

# # 環境変数の読み込み
# load_dotenv()

# # データベース接続情報
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_HOST = os.getenv('DB_HOST')
# DB_PORT = os.getenv('DB_PORT')
# DB_NAME = os.getenv('DB_NAME')

# # MySQLのURL構築
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# # エンジンの作成
# engine = create_engine(
#     DATABASE_URL,
#     echo=True,
#     pool_pre_ping=True,
#     pool_recycle=3600
# )
