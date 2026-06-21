from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI() #產生 FastAPI 物件
# 利用uvicorn 去啟動伺服器在 http://127.0.0.1:8000
# 利用路由的設定，處理路徑/
@app.get("/")
def index():
    return {"data":"Home Page"}
#利用路由的設定，處理路徑/data
# @app.get("/data")
# def getData():
#     return {"data":[2,3,1]}

# 動態路由練習
# 想要讓前端可以透過網址，輸入一個數字，後端把輸入的數字做平分，再回應給前端
# 使用路徑參數，處理有相同前贅字/square/任意的整數 的路徑
@app.get("/square/{num}")
def square(num:Annotated[int,Path(ge=1,le=30)]):
    num=int(num)
    result=num*num
    return{"result":result}

#要求字串練習
#處理路徑 /hello?name=名字
@app.get("/hello")
def hello(name):
    message="Hello，"+name
    return {"message":message}

#處理路徑 /multiply?n1=數字&n2=數字
@app.get("/multiply")
def multiply(
    n1:Annotated[int,Query(ge=0,le=10)],
    n2:Annotated[int,Query(ge=0,le=10)]
):  
    n1=int(n1)
    n2=int(n2)
    result=n1*n2
    return {"result":result}

#處理路徑 /echo/名字
@app.get("/echo/{name}")
def echo(name:Annotated[str,Path(min_length=2,max_length=30)]):
    return{"message":"Hello "+ name}
