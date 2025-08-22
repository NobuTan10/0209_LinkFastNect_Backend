# app.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json

# モデル/CRUD（import時にDBへ接続・create_allを走らせないことが重要）
from db_control import crud, mymodels

# ★ 追加：起動時にだけテーブル作成する関数を呼ぶ
from db_control.create_tables import init_db

class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str

app = FastAPI()

# CORS（必要に応じて許可ドメインを絞る）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では指定推奨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ★ 追加：アプリ起動時にDB初期化（create_all）を実行
@app.on_event("startup")
def on_startup():
    init_db()  # ← ここで初めてDBに触る

# ★ 追加：単純ヘルスチェック（DBに触らない）
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/")
def index():
    return {"message": "FastAPI top page!"}

@app.post("/customers")
def create_customer(customer: Customer):
    values = customer.dict()
    crud.myinsert(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))
    if result:
        return json.loads(result) or None
    return None

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
    crud.myupdate(mymodels.Customers, values)
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


from sqlalchemy import text as sql_text
from db_control.connect_MySQL import engine

@app.get("/db-healthz")
def db_healthz():
    with engine.connect() as conn:
        conn.execute(sql_text("SELECT 1"))
    return {"db": "ok"}
