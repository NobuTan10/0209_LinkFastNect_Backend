from sqlalchemy import create_engine
# import sqlalchemy

import os
SSL_CA_PATH = os.getenv("SSL_CA_PATH", "DigiCertGlobalRootCA.crt.pem")
# 例: mysql.connector.connect(..., ssl_ca=SSL_CA_PATH)

# uname() error回避
import platform
print("platform:", platform.uname())


main_path = os.path.dirname(os.path.abspath(__file__))
path = os.chdir(main_path)
print("path:", path)
engine = create_engine("sqlite:///CRM.db", echo=True)
