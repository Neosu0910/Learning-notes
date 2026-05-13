# Python 語法入門筆記

> 給完全沒寫過 Python 的新手。每個概念都有對應的 JavaScript 比較，方便理解。

---

## 1. 變數（Variables）

Python 宣告變數**不需要關鍵字**，直接寫就好。

```python
# Python
name = "Alice"
age = 25
price = 9.99
is_active = True
nothing = None
```

```javascript
// JavaScript 對應
let name = "Alice";
let age = 25;
let price = 9.99;
let isActive = true;
let nothing = null;
```

### 常見資料型別

| Python | 說明 | 範例 |
|--------|------|------|
| `str` | 字串 | `"hello"` |
| `int` | 整數 | `42` |
| `float` | 浮點數 | `3.14` |
| `bool` | 布林值 | `True` / `False`（注意大寫） |
| `None` | 空值 | `None`（對應 JS 的 `null`） |

```python
# 查看型別
print(type("hello"))   # <class 'str'>
print(type(42))        # <class 'int'>
print(type(True))      # <class 'bool'>
```

---

## 2. 字串（Strings）

```python
name = "Alice"

# 字串拼接
greeting = "Hello, " + name        # "Hello, Alice"

# f-string（最常用，類似 JS 的 template literal）
greeting = f"Hello, {name}!"       # "Hello, Alice!"
greeting = f"1 + 1 = {1 + 1}"     # "1 + 1 = 2"

# 常用方法
"hello".upper()        # "HELLO"
"HELLO".lower()        # "hello"
"  hello  ".strip()    # "hello"（去除前後空白）
"hello".replace("l", "r")  # "herro"
"a,b,c".split(",")     # ["a", "b", "c"]
```

```javascript
// JavaScript 對應
const greeting = `Hello, ${name}!`;  // template literal
```

---

## 3. 條件判斷（if / elif / else）

Python 用**縮排**（indent）表示程式碼區塊，不用大括號 `{}`。

```python
age = 20

if age >= 18:
    print("成年")
elif age >= 13:
    print("青少年")
else:
    print("兒童")
```

```javascript
// JavaScript 對應
if (age >= 18) {
    console.log("成年");
} else if (age >= 13) {
    console.log("青少年");
} else {
    console.log("兒童");
}
```

### 比較運算子

| Python | 說明 |
|--------|------|
| `==` | 等於 |
| `!=` | 不等於 |
| `>` / `<` | 大於 / 小於 |
| `>=` / `<=` | 大於等於 / 小於等於 |
| `and` | 且（JS 的 `&&`） |
| `or` | 或（JS 的 `\|\|`） |
| `not` | 非（JS 的 `!`） |
| `in` | 包含（JS 沒有直接對應） |

```python
# in 的用法
fruits = ["apple", "banana"]
if "apple" in fruits:
    print("有蘋果")

name = "Alice"
if "li" in name:
    print("名字包含 li")
```

---

## 4. 迴圈（Loops）

### for 迴圈

```python
# 遍歷 list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
# apple
# banana
# cherry

# 跑數字範圍（range）
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):    # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8（每次加 2）
    print(i)
```

```javascript
// JavaScript 對應
for (let i = 0; i < 5; i++) { ... }
fruits.forEach(fruit => console.log(fruit));
```

### while 迴圈

```python
count = 0
while count < 3:
    print(count)
    count += 1
# 0
# 1
# 2
```

### break / continue

```python
for i in range(10):
    if i == 3:
        break       # 跳出迴圈
    print(i)
# 0, 1, 2

for i in range(5):
    if i == 2:
        continue    # 跳過這次，繼續下一圈
    print(i)
# 0, 1, 3, 4
```

---

## 5. 函式（Functions）

```python
# 定義函式
def greet(name):
    return f"Hello, {name}!"

# 呼叫函式
result = greet("Alice")
print(result)  # Hello, Alice!
```

```javascript
// JavaScript 對應
function greet(name) {
    return `Hello, ${name}!`;
}
```

### 預設參數

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Alice")              # "Hello, Alice!"
greet("Alice", "Hi")        # "Hi, Alice!"
greet("Alice", greeting="Hey")  # "Hey, Alice!"（關鍵字參數）
```

### 多個回傳值

```python
def get_min_max(numbers):
    return min(numbers), max(numbers)  # 回傳 tuple

low, high = get_min_max([3, 1, 4, 1, 5])
print(low)   # 1
print(high)  # 5
```

---

## 6. List（清單）

類似 JavaScript 的 Array。

```python
fruits = ["apple", "banana", "cherry"]

# 存取
fruits[0]    # "apple"（第一個）
fruits[-1]   # "cherry"（最後一個）

# 切片（slice）
fruits[0:2]  # ["apple", "banana"]（index 0 到 1）
fruits[1:]   # ["banana", "cherry"]（從 index 1 到結尾）

# 新增
fruits.append("date")       # 加到最後
fruits.insert(1, "avocado") # 插入到 index 1

# 刪除
fruits.remove("banana")     # 刪除指定值
fruits.pop()                # 刪除最後一個
fruits.pop(0)               # 刪除 index 0

# 長度
len(fruits)  # 元素數量

# 排序
fruits.sort()               # 原地排序（修改原 list）
sorted(fruits)              # 回傳新的排序 list（不修改原本）
```

### List Comprehension（常用！）

用一行建立 list，類似 JS 的 `.map()` + `.filter()`：

```python
numbers = [1, 2, 3, 4, 5]

# 每個數字乘以 2（類似 JS 的 .map()）
doubled = [n * 2 for n in numbers]
# [2, 4, 6, 8, 10]

# 只取偶數（類似 JS 的 .filter()）
evens = [n for n in numbers if n % 2 == 0]
# [2, 4]

# 組合：取偶數並乘以 2
result = [n * 2 for n in numbers if n % 2 == 0]
# [4, 8]
```

---

## 7. Dictionary（字典）

類似 JavaScript 的 Object。

```python
user = {
    "name": "Alice",
    "age": 25,
    "email": "alice@example.com"
}

# 存取
user["name"]          # "Alice"
user.get("name")      # "Alice"（不存在時回傳 None，不會報錯）
user.get("phone", "無") # "無"（不存在時回傳預設值）

# 新增 / 修改
user["phone"] = "0912345678"
user["age"] = 26

# 刪除
del user["phone"]

# 檢查 key 是否存在
"name" in user   # True
"phone" in user  # False

# 遍歷
for key in user:
    print(key, user[key])

for key, value in user.items():
    print(f"{key}: {value}")

# 所有 key / value
user.keys()    # dict_keys(["name", "age", "email"])
user.values()  # dict_values(["Alice", 25, "alice@example.com"])
```

---

## 8. Tuple（元組）

像 List 但**不可修改**，用小括號。

```python
point = (10, 20)
x, y = point   # 解構（unpacking）
print(x)  # 10
print(y)  # 20

# 常用在函式回傳多個值
def get_size():
    return 1920, 1080  # 其實是回傳 tuple

width, height = get_size()
```

---

## 9. 類別（Class）

類似 JavaScript 的 `class`，但語法不同。

```python
class Dog:
    # __init__ 是建構子（類似 JS 的 constructor）
    def __init__(self, name, age):
        self.name = name   # self 類似 JS 的 this
        self.age = age

    def bark(self):
        return f"{self.name} says: Woof!"

    def __str__(self):
        return f"Dog({self.name}, {self.age})"  # print 時顯示的內容

# 建立實例
dog = Dog("Rex", 3)
print(dog.name)    # Rex
print(dog.bark())  # Rex says: Woof!
print(dog)         # Dog(Rex, 3)
```

```javascript
// JavaScript 對應
class Dog {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    bark() {
        return `${this.name} says: Woof!`;
    }
}
```

---

## 10. 錯誤處理（try / except）

```python
# 類似 JS 的 try / catch
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零！")

try:
    number = int("abc")   # 轉換失敗
except ValueError as e:
    print(f"錯誤：{e}")
finally:
    print("不管有沒有錯誤都會執行")
```

```javascript
// JavaScript 對應
try {
    ...
} catch (e) {
    console.log(e);
} finally {
    ...
}
```

---

## 11. 模組與 import

```python
# 引入標準函式庫
import math
print(math.sqrt(16))   # 4.0
print(math.pi)         # 3.14159...

# 只引入特定函式
from math import sqrt, pi
print(sqrt(16))        # 4.0

# 引入並取別名
import numpy as np     # 常見慣例

# 引入自己寫的檔案
from utils import helper_function   # 引入 utils.py 裡的函式
from models import User             # 引入 models.py 裡的 class
```

---

## 12. 常用內建函式

```python
# 型別轉換
int("42")       # 42
str(42)         # "42"
float("3.14")   # 3.14
list((1, 2, 3)) # [1, 2, 3]

# 數學
abs(-5)         # 5（絕對值）
max(1, 2, 3)    # 3
min(1, 2, 3)    # 1
sum([1, 2, 3])  # 6
round(3.14159, 2)  # 3.14

# 序列
len([1, 2, 3])  # 3
range(5)        # 0, 1, 2, 3, 4
enumerate(["a", "b", "c"])  # (0, "a"), (1, "b"), (2, "c")
zip([1, 2], ["a", "b"])     # (1, "a"), (2, "b")

# enumerate 實際用法
fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry

# 輸出
print("Hello")
print("a", "b", "c")          # a b c
print("a", "b", sep=", ")     # a, b
```

---

## 13. Python 特有習慣（跟 JS 不同的地方）

| 概念 | Python | JavaScript |
|------|--------|-----------|
| 縮排 | 強制，用縮排表示區塊 | 用 `{}` |
| 命名慣例 | `snake_case`（底線） | `camelCase`（駝峰） |
| 布林值 | `True` / `False`（大寫） | `true` / `false`（小寫） |
| 空值 | `None` | `null` / `undefined` |
| 字串 | `"..."` 或 `'...'` 都可以 | 同左 |
| 行尾 | 不需要 `;` | 通常加 `;` |
| 註解 | `# 單行` | `// 單行` |
| 多行註解 | `"""多行"""` | `/* 多行 */` |

---

## 重點整理

- Python 用**縮排**表示程式碼區塊（不用 `{}`）
- 變數宣告不需要 `let`/`const`，直接 `x = 1`
- `def` 定義函式（對應 JS 的 `function`）
- `True`/`False`/`None` 首字母大寫
- List = Array，Dictionary = Object
- f-string 是字串格式化的最佳選擇：`f"Hello, {name}"`
- `self` 在 class 裡等同於 JS 的 `this`

---

## 14. Pydantic（資料驗證與型別強制）

Pydantic 是 Python 最常用的資料驗證函式庫，FastAPI 底層就是用它來處理 request/response 的型別驗證。核心概念是：**用 Python 的 type hint 定義資料結構，Pydantic 自動幫你驗證和轉換資料**。

```bash
pip install pydantic
```

---

### 基本用法：BaseModel

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool = True  # 有預設值，可以不傳

# 建立實例（自動驗證）
user = User(name="Alice", age=25, email="alice@example.com")
print(user.name)      # Alice
print(user.age)       # 25
print(user.is_active) # True（預設值）

# 自動型別轉換（coercion）
user2 = User(name="Bob", age="30", email="bob@example.com")
# age 傳了字串 "30"，Pydantic 自動轉成 int 30
print(type(user2.age))  # <class 'int'>

# 驗證失敗會拋出 ValidationError
try:
    bad_user = User(name="Charlie", age="not_a_number", email="c@c.com")
except Exception as e:
    print(e)
# age: Input should be a valid integer...
```

```javascript
// JavaScript 沒有內建等效工具，通常用 Zod 或 Joi
import { z } from "zod";
const UserSchema = z.object({
    name: z.string(),
    age: z.number(),
    email: z.string().email(),
});
```

---

### Optional 欄位與 None

```python
from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None  # 可以是 str 或 None，預設 None

p1 = Product(name="Apple", price=1.5)
print(p1.description)  # None

p2 = Product(name="Banana", price=0.8, description="Fresh banana")
print(p2.description)  # Fresh banana
```

Python 3.10+ 可以用更簡潔的寫法：
```python
class Product(BaseModel):
    description: str | None = None  # 等同於 Optional[str] = None
```

---

### 巢狀 Model（Nested Model）

「巢狀」的意思是：一個 model 的某個欄位，它的型別是**另一個 model**，而不是單純的 `str` 或 `int`。

先定義三個獨立的 model，每個 model 就像一張表單，有自己的欄位：

```python
from pydantic import BaseModel
from typing import List

# 表單一：地址（有 city 和 country 兩個欄位）
class Address(BaseModel):
    city: str
    country: str

# 表單二：訂單（有 item 和 quantity 兩個欄位）
class Order(BaseModel):
    item: str      # 買什麼商品
    quantity: int  # 買幾個

# 表單三：使用者（address 欄位的型別是 Address model，不是 str）
class User(BaseModel):
    name: str
    address: Address          # 這個欄位要填一個 Address 物件
    orders: List[Order] = []  # 這個欄位是一個 list，裡面每個元素都是 Order 物件
```

建立 User 時，`address` 和 `orders` 可以直接傳 **dict**，Pydantic 會自動幫你轉換：

```python
user = User(
    name="Alice",
    # address 欄位型別是 Address，傳入 dict，Pydantic 自動轉成 Address 物件
    address={"city": "Taipei", "country": "Taiwan"},
    # orders 欄位是 List[Order]，傳入 dict 的 list
    # 每個 dict 對應 Order 的欄位：item（買什麼）和 quantity（買幾個）
    orders=[
        {"item": "Book", "quantity": 2},   # 買 2 本書
        {"item": "Pen",  "quantity": 5},   # 買 5 支筆
    ]
)
```

存取資料時，用 `.` 一層一層往下取：

```python
print(user.name)              # Alice
print(user.address.city)      # Taipei（address 是 Address 物件，再取 .city）
print(user.address.country)   # Taiwan
print(user.orders[0].item)    # Book（orders[0] 是第一個 Order 物件，取 .item）
print(user.orders[0].quantity)# 2
print(user.orders[1].item)    # Pen
print(user.orders[1].quantity)# 5

# 注意：address 已經是 Address 物件，不是原本的 dict
print(type(user.address))     # <class '__main__.Address'>
print(type(user.orders[0]))   # <class '__main__.Order'>
```

也可以先建好物件再傳入，效果完全一樣：

```python
# 方法一：直接傳 dict（上面的做法）
user = User(name="Alice", address={"city": "Taipei", "country": "Taiwan"}, ...)

# 方法二：先建好 Address 物件再傳入
addr = Address(city="Taipei", country="Taiwan")
user = User(name="Alice", address=addr, ...)
# 兩種寫法結果完全相同，方法一比較簡潔
```

---

### Field：欄位細部設定

`Field` 讓你對每個欄位加上更多限制和說明：

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="商品名稱")
    price: float = Field(gt=0, description="價格，必須大於 0")
    quantity: int = Field(ge=0, le=9999, description="庫存數量")
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$", description="格式：ABC-1234")

# 驗證
try:
    p = Product(name="", price=-10, quantity=99999, sku="invalid")
except Exception as e:
    print(e)
```

常用的 Field 限制：

| 參數 | 說明 | 適用型別 |
|------|------|----------|
| `min_length` / `max_length` | 字串長度限制 | `str` |
| `gt` / `ge` | 大於 / 大於等於 | `int`, `float` |
| `lt` / `le` | 小於 / 小於等於 | `int`, `float` |
| `pattern` | 正規表達式驗證 | `str` |
| `default` | 預設值 | 所有型別 |
| `description` | 欄位說明（會出現在 API 文件） | 所有型別 |
| `alias` | 欄位別名（接收不同名稱的 key） | 所有型別 |

---

### validator：自訂驗證邏輯

當內建的限制不夠用時，用 `@field_validator` 寫自訂驗證：

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int
    email: str

    @field_validator("age")
    @classmethod
    def age_must_be_adult(cls, v):
        if v < 18:
            raise ValueError("必須年滿 18 歲")
        return v

    @field_validator("email")
    @classmethod
    def email_must_have_at(cls, v):
        if "@" not in v:
            raise ValueError("Email 格式不正確")
        return v.lower()  # 順便轉小寫

# 測試
try:
    u = User(name="Alice", age=16, email="alice@example.com")
except Exception as e:
    print(e)  # age: 必須年滿 18 歲

u2 = User(name="Bob", age=25, email="BOB@EXAMPLE.COM")
print(u2.email)  # bob@example.com（自動轉小寫）
```

---

### model_validator：跨欄位驗證

需要同時看多個欄位才能驗證時用 `@model_validator`：

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def check_date_order(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date 必須早於 end_date")
        return self

# 測試
try:
    r = DateRange(start_date="2026-05-10", end_date="2026-05-01")
except Exception as e:
    print(e)  # start_date 必須早於 end_date
```

---

### 序列化：轉成 dict 和 JSON

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

user = User(name="Alice", age=25, email="alice@example.com")

# 轉成 dict
user_dict = user.model_dump()
print(user_dict)
# {"name": "Alice", "age": 25, "email": "alice@example.com"}

# 轉成 JSON 字串
user_json = user.model_dump_json()
print(user_json)
# '{"name":"Alice","age":25,"email":"alice@example.com"}'

# 排除特定欄位
user.model_dump(exclude={"email"})
# {"name": "Alice", "age": 25}

# 只包含特定欄位
user.model_dump(include={"name", "age"})
# {"name": "Alice", "age": 25}
```

---

### 從 dict / JSON 建立 Model

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# 從 dict 建立
data = {"name": "Alice", "age": 25}
user = User.model_validate(data)

# 從 JSON 字串建立
json_str = '{"name": "Bob", "age": 30}'
user2 = User.model_validate_json(json_str)

print(user.name)   # Alice
print(user2.name)  # Bob
```

---

### 在 FastAPI 裡的應用

Pydantic 和 FastAPI 是天生一對，FastAPI 用 Pydantic model 來：
1. 驗證 request body
2. 自動產生 API 文件（Swagger UI）
3. 序列化 response

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Request model（接收前端傳來的資料）
class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str

# Response model（回傳給前端的資料）
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # 注意：不包含 age，不想讓前端看到

@app.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest):
    # FastAPI 自動驗證 request body，不合法直接回 422
    # user 已經是驗證過的 Pydantic model
    new_user = save_to_db(user)  # 假設這個函式存到 DB 並回傳含 id 的資料
    return UserResponse(id=new_user.id, name=user.name, email=user.email)
```

---

### Pydantic v1 vs v2 差異

Pydantic v2（2023 年後）有些語法改變，常見的：

| 功能 | v1 寫法 | v2 寫法 |
|------|---------|---------|
| 轉成 dict | `.dict()` | `.model_dump()` |
| 轉成 JSON | `.json()` | `.model_dump_json()` |
| 從 dict 建立 | `.parse_obj()` | `.model_validate()` |
| 從 JSON 建立 | `.parse_raw()` | `.model_validate_json()` |
| 欄位驗證器 | `@validator` | `@field_validator` |
| Model 驗證器 | `@root_validator` | `@model_validator` |

> FastAPI 0.100+ 預設使用 Pydantic v2，新專案直接用 v2 語法就好。

---

### 重點整理

- `BaseModel` 是核心，繼承它來定義資料結構
- Pydantic 會自動做**型別轉換**（`"30"` → `30`）和**驗證**
- `Optional[str] = None` 表示欄位可以是 None
- `Field(gt=0, min_length=1)` 加上細部限制
- `@field_validator` 寫自訂驗證邏輯
- `.model_dump()` 轉 dict，`.model_dump_json()` 轉 JSON 字串
- FastAPI 裡用 Pydantic model 當 request/response 型別，自動驗證 + 產生文件
