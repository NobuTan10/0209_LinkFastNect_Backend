# app.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import json
import os
import os.path

# DB接続 & SQLユーティリティ
from sqlalchemy import text as sql_text
from db_control.connect_MySQL import engine

# モデル/CRUD（import時に create_all を走らせないことが重要）
from db_control import crud, mymodels
from db_control.create_tables import init_db  # 起動時だけ create_all を実行

# -------------------------
# Pydantic models
# -------------------------
class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI()

# CORS（必要に応じて許可ドメインを絞ってください）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 本番では特定ドメインに絞る推奨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Lifecycle
# -------------------------
@app.on_event("startup")
def on_startup():
    # 起動時に初回だけテーブル作成（import時には走らない）
    init_db()

# -------------------------
# Health / Diag
# -------------------------
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/diag")
def diag():
    """環境変数とSSL証明書の有無を簡易確認"""
    ssl_path = os.getenv("MYSQL_SSL_CA", "/home/site/wwwroot/DigiCertGlobalRootCA.crt.pem")
    return {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_PORT": os.getenv("DB_PORT"),
        "SSL_CA": ssl_path,
        "SSL_CA_exists": os.path.exists(ssl_path),
    }

@app.get("/db-healthz")
def db_healthz():
    """DB到達チェック（例外はJSONで返す：原因特定用）"""
    try:
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        # 一時的に例外を返して原因を可視化（デバッグ後は200だけ返す実装に戻してOK）
        print("DB_HEALTHZ_ERROR:", repr(e))
        return JSONResponse(
            status_code=500,
            content={"error": type(e).__name__, "message": str(e)},
        )

# -------------------------
# Routes
# -------------------------
@app.get("/")
def index():
    return {"message": "FastAPI top page!"}

@app.post("/customers", status_code=201)
def create_customer(customer: Customer):
    values = customer.dict()
    ok = crud.myinsert(mymodels.Customers, values)
    if not ok:
        raise HTTPException(status_code=500, detail="E0100: insert failed")
    # 登録結果（確認のために再取得して返却）
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))
    return (json.loads(result) or [values])[0]

@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    result = crud.myselect(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None

@app.get("/allcustomers")
def read_all_customer():
    result = crud.myselectAll(mymodels.Customers)
    return [] if not result else json.loads(result)

@app.put("/customers")
def update_customer(customer: Customer):
    values = customer.dict()
    ok = crud.myupdate(mymodels.Customers, values)
    if not ok:
        raise HTTPException(status_code=500, detail="E0200: update failed")
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None

@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    ok = crud.mydelete(mymodels.Customers, customer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_id, "status": "deleted"}

@app.get("/fetchtest")
def fetchtest():
    response = requests.get("https://jsonplaceholder.typicode.com/users", timeout=10)
    return response.json()
