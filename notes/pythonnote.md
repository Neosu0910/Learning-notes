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


---

## 15. `__init__` 與 Magic Methods（魔術方法）

### `__init__` 是什麼？

`__init__` 是 Python class 的**初始化方法**（Initializer），在你用 `ClassName()` 建立物件時**自動被呼叫**。它的作用是設定物件的初始狀態（屬性）。

> 注意：`__init__` 嚴格來說不是「建構子（constructor）」，真正建立物件的是 `__new__`。但實務上你可以把 `__init__` 當作建構子來理解，99% 的情況只需要用 `__init__`。

```python
class User:
    def __init__(self, name, age):
        # self 是正在被建立的物件本身（類似 JS 的 this）
        self.name = name   # 把傳入的 name 存到物件的 .name 屬性
        self.age = age     # 把傳入的 age 存到物件的 .age 屬性
        self.is_active = True  # 也可以設定不需要傳入的預設屬性

# 建立物件時，Python 自動呼叫 __init__
user = User("Alice", 25)
# 等同於：先建立空物件，再呼叫 User.__init__(空物件, "Alice", 25)

print(user.name)       # Alice
print(user.age)        # 25
print(user.is_active)  # True
```

```javascript
// JavaScript 對應
class User {
    constructor(name, age) {
        this.name = name;
        this.age = age;
        this.isActive = true;
    }
}
```

---

### `__init__` 的常見模式

```python
# 1. 帶預設值的 __init__
class Config:
    def __init__(self, host="localhost", port=8080, debug=False):
        self.host = host
        self.port = port
        self.debug = debug

config = Config()                        # 全部用預設值
config2 = Config(port=3000, debug=True)  # 只改部分

# 2. 在 __init__ 裡做驗證
class Age:
    def __init__(self, value):
        if value < 0:
            raise ValueError("年齡不能為負數")
        self.value = value

# 3. 在 __init__ 裡初始化其他資源
class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.pool = []           # 初始化連線池
        self._is_connected = False  # 私有屬性（慣例用底線開頭）
```

---

### 其他常用 Magic Methods

Python 用 **雙底線包起來** 的方法（dunder methods）讓你自訂物件的行為：

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        """print() 時顯示的字串"""
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):
        """開發時顯示的字串（在 REPL 或 debug 時）"""
        return f"Vector(x={self.x}, y={self.y})"

    def __add__(self, other):
        """讓兩個 Vector 可以用 + 相加"""
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        """定義 == 比較的邏輯"""
        return self.x == other.x and self.y == other.y

    def __len__(self):
        """讓 len() 可以用在這個物件上"""
        return int((self.x**2 + self.y**2) ** 0.5)

v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1)          # Vector(1, 2)      → 呼叫 __str__
print(v1 + v2)    # Vector(4, 6)      → 呼叫 __add__
print(v1 == v2)   # False             → 呼叫 __eq__
print(len(v2))    # 5                 → 呼叫 __len__
```

### 常用 Magic Methods 速查

| 方法 | 觸發時機 | 用途 |
|------|----------|------|
| `__init__` | `ClassName()` 建立物件時 | 初始化屬性 |
| `__str__` | `print(obj)` 或 `str(obj)` | 使用者友善的字串表示 |
| `__repr__` | 在 REPL 或 `repr(obj)` | 開發者用的字串表示 |
| `__add__` | `obj1 + obj2` | 自訂加法 |
| `__eq__` | `obj1 == obj2` | 自訂相等比較 |
| `__lt__` | `obj1 < obj2` | 自訂小於比較 |
| `__len__` | `len(obj)` | 自訂長度 |
| `__getitem__` | `obj[key]` | 自訂索引存取 |
| `__contains__` | `x in obj` | 自訂 `in` 運算 |
| `__enter__` / `__exit__` | `with obj:` | Context Manager |

---

## 16. Async / Await（非同步程式設計）

### 為什麼需要 async？

當程式需要等待 I/O 操作（讀檔案、呼叫 API、查資料庫）時，同步程式會**卡住**直到操作完成。async 讓程式在等待期間可以去做其他事情，不浪費時間。

```python
# 同步：一個一個等，很慢
import time

def fetch_data():
    time.sleep(2)  # 模擬等待 2 秒
    return "data"

# 依序執行 3 次 = 等 6 秒
result1 = fetch_data()
result2 = fetch_data()
result3 = fetch_data()
```

```python
# 非同步：同時等待，快很多
import asyncio

async def fetch_data():
    await asyncio.sleep(2)  # 非同步等待 2 秒（不卡住）
    return "data"

async def main():
    # 同時發出 3 個請求，只等 2 秒（不是 6 秒）
    results = await asyncio.gather(
        fetch_data(),
        fetch_data(),
        fetch_data()
    )
    print(results)  # ["data", "data", "data"]

asyncio.run(main())
```

---

### 基本語法

```python
import asyncio

# 用 async def 定義非同步函式（coroutine）
async def greet(name):
    print(f"開始跟 {name} 打招呼...")
    await asyncio.sleep(1)   # 模擬等待，讓出控制權
    print(f"Hello, {name}!")
    return f"greeted {name}"

# 執行 coroutine 的方式
async def main():
    result = await greet("Alice")  # await 等待 coroutine 完成
    print(result)  # "greeted Alice"

# 程式進入點
asyncio.run(main())
```

```javascript
// JavaScript 對應（幾乎一模一樣）
async function greet(name) {
    console.log(`開始跟 ${name} 打招呼...`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log(`Hello, ${name}!`);
    return `greeted ${name}`;
}

async function main() {
    const result = await greet("Alice");
    console.log(result);
}
main();
```

---

### 並發執行多個任務

```python
import asyncio

async def fetch_user(user_id):
    await asyncio.sleep(1)  # 模擬 API 呼叫
    return {"id": user_id, "name": f"User_{user_id}"}

async def fetch_orders(user_id):
    await asyncio.sleep(1.5)  # 模擬 DB 查詢
    return [{"order_id": 1, "amount": 100}]

async def main():
    # 方法一：asyncio.gather（同時執行，等全部完成）
    user, orders = await asyncio.gather(
        fetch_user(1),
        fetch_orders(1)
    )
    print(user)    # {"id": 1, "name": "User_1"}
    print(orders)  # [{"order_id": 1, "amount": 100}]
    # 總共只等 1.5 秒（取最慢的那個），不是 2.5 秒

    # 方法二：asyncio.create_task（建立任務，稍後 await）
    task1 = asyncio.create_task(fetch_user(2))
    task2 = asyncio.create_task(fetch_orders(2))
    # 這兩個任務已經開始跑了
    # 做一些其他事情...
    user2 = await task1   # 取得結果
    orders2 = await task2

asyncio.run(main())
```

```javascript
// JavaScript 對應
const [user, orders] = await Promise.all([
    fetchUser(1),
    fetchOrders(1)
]);
```

---

### 在 FastAPI 裡的 async

FastAPI 天生支援 async，大部分路由都建議用 async：

```python
from fastapi import FastAPI
import httpx  # 非同步 HTTP client（像 axios）

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # 用 async HTTP client 呼叫其他 API
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
    return response.json()

@app.get("/dashboard")
async def get_dashboard():
    # 同時查詢多個資料來源
    async with httpx.AsyncClient() as client:
        users, orders, stats = await asyncio.gather(
            client.get("https://api.example.com/users"),
            client.get("https://api.example.com/orders"),
            client.get("https://api.example.com/stats"),
        )
    return {
        "users": users.json(),
        "orders": orders.json(),
        "stats": stats.json()
    }
```

---

### async 重點整理

| 概念 | Python | JavaScript |
|------|--------|-----------|
| 定義非同步函式 | `async def fn()` | `async function fn()` |
| 等待結果 | `await coroutine` | `await promise` |
| 同時執行多個 | `asyncio.gather(...)` | `Promise.all([...])` |
| 執行進入點 | `asyncio.run(main())` | 直接 `await`（top-level await） |
| 非同步 sleep | `await asyncio.sleep(1)` | `await new Promise(r => setTimeout(r, 1000))` |
| 非同步 for 迴圈 | `async for item in ...` | `for await (const item of ...)` |

---

## 17. Generator（產生器）

### Generator 是什麼？

Generator 是一種特殊的函式，它**不會一次把所有結果算完再回傳**，而是每次被呼叫時只**產出（yield）一個值**，然後暫停，等下次被要求時再繼續。

好處：**省記憶體**。如果你有一百萬筆資料，普通函式會一次建立一個一百萬元素的 list；Generator 一次只產生一個，用多少拿多少。

```python
# 普通函式：一次回傳所有結果（佔大量記憶體）
def get_squares_list(n):
    result = []
    for i in range(n):
        result.append(i ** 2)
    return result

# Generator：每次只產出一個（省記憶體）
def get_squares_gen(n):
    for i in range(n):
        yield i ** 2  # yield 就像 return，但函式不會結束，只是暫停

# 使用方式看起來一樣
for num in get_squares_list(5):
    print(num)  # 0, 1, 4, 9, 16

for num in get_squares_gen(5):
    print(num)  # 0, 1, 4, 9, 16（效果一樣，但記憶體用量極小）
```

```javascript
// JavaScript Generator 對應
function* getSquaresGen(n) {
    for (let i = 0; i < n; i++) {
        yield i ** 2;
    }
}

for (const num of getSquaresGen(5)) {
    console.log(num);  // 0, 1, 4, 9, 16
}
```

---

### Generator 的運作流程

```python
def countdown(n):
    print("開始倒數！")
    while n > 0:
        yield n          # 暫停，把 n 交出去
        n -= 1           # 下次繼續時從這裡開始
    print("倒數結束！")

gen = countdown(3)       # 建立 generator 物件（還沒開始執行）

print(next(gen))  # 印出「開始倒數！」，然後 yield 3 → 輸出 3
print(next(gen))  # 繼續執行，yield 2 → 輸出 2
print(next(gen))  # 繼續執行，yield 1 → 輸出 1
# print(next(gen))  # 印出「倒數結束！」，然後拋出 StopIteration

# 通常不會手動呼叫 next()，而是用 for 迴圈
for num in countdown(3):
    print(num)  # 3, 2, 1（for 迴圈自動處理 StopIteration）
```

---

### Generator Expression（產生器表達式）

類似 List Comprehension，但用小括號 `()`，產出的是 generator 而非 list：

```python
# List Comprehension → 一次建立整個 list，佔記憶體
squares_list = [x**2 for x in range(1000000)]  # 佔用大量記憶體

# Generator Expression → 需要時才計算，幾乎不佔記憶體
squares_gen = (x**2 for x in range(1000000))   # 幾乎不佔記憶體

# 可以用在任何接受 iterable 的地方
total = sum(x**2 for x in range(1000000))  # 直接傳入 sum()，不用額外的括號
```

---

### 實際應用場景

```python
# 1. 讀取大檔案（一行一行讀，不會把整個檔案載入記憶體）
def read_large_file(file_path):
    with open(file_path, "r") as f:
        for line in f:
            yield line.strip()

for line in read_large_file("huge_log.txt"):
    if "ERROR" in line:
        print(line)

# 2. 分頁查詢資料庫
def fetch_all_users(page_size=100):
    offset = 0
    while True:
        users = db.query(f"SELECT * FROM users LIMIT {page_size} OFFSET {offset}")
        if not users:
            break
        for user in users:
            yield user
        offset += page_size

# 不管有幾百萬筆，記憶體裡一次只有 100 筆
for user in fetch_all_users():
    process(user)

# 3. 無限序列（Fibonacci）
def fibonacci():
    a, b = 0, 1
    while True:  # 無限產生，不會爆記憶體
        yield a
        a, b = b, a + b

# 取前 10 個 Fibonacci 數
from itertools import islice
first_10 = list(islice(fibonacci(), 10))
print(first_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

### yield from（委派 Generator）

`yield from` 讓你把另一個 generator 的所有值「轉發」出去：

```python
def gen_numbers():
    yield from range(3)      # 0, 1, 2
    yield from range(10, 13) # 10, 11, 12

list(gen_numbers())  # [0, 1, 2, 10, 11, 12]

# 等同於：
def gen_numbers_verbose():
    for i in range(3):
        yield i
    for i in range(10, 13):
        yield i
```

---

## 18. Decorator（裝飾器）

### Decorator 是什麼？

Decorator 是一種**包裝函式的函式**，讓你在不修改原本函式程式碼的情況下，**新增額外的行為**（例如記錄日誌、驗證權限、計時等）。

語法是在函式上方加 `@decorator_name`。

```python
# 最簡單的 decorator 範例：計時器
import time

def timer(func):
    """包裝函式，加上計時功能"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)  # 呼叫原本的函式
        end = time.time()
        print(f"{func.__name__} 花了 {end - start:.2f} 秒")
        return result
    return wrapper

# 使用 decorator
@timer
def slow_function():
    time.sleep(1)
    return "done"

result = slow_function()
# 印出：slow_function 花了 1.00 秒
print(result)  # "done"
```

`@timer` 等同於 `slow_function = timer(slow_function)`，只是語法糖。

```javascript
// JavaScript 沒有原生 decorator 語法（TC39 Stage 3 提案中）
// 但概念上等同於 Higher-Order Function：
function timer(fn) {
    return function(...args) {
        const start = Date.now();
        const result = fn(...args);
        console.log(`${fn.name} 花了 ${Date.now() - start}ms`);
        return result;
    };
}
const slowFunction = timer(function slowFunction() { ... });
```

---

### Decorator 運作原理拆解

```python
def my_decorator(func):
    print(f"正在裝飾 {func.__name__}")  # 裝飾時就會執行

    def wrapper(*args, **kwargs):
        print("--- 函式執行前 ---")
        result = func(*args, **kwargs)   # 呼叫原本的函式
        print("--- 函式執行後 ---")
        return result

    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}!")

# 載入時印出：正在裝飾 say_hello

say_hello("Alice")
# --- 函式執行前 ---
# Hello, Alice!
# --- 函式執行後 ---
```

---

### 帶參數的 Decorator

如果 decorator 本身也需要接收參數，要多包一層：

```python
def repeat(times):
    """讓函式重複執行 n 次"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say_hi():
    print("Hi!")

say_hi()
# Hi!
# Hi!
# Hi!
```

---

### 用 functools.wraps 保留原函式資訊

Decorator 會讓原函式的 `__name__`、`__doc__` 消失（被 wrapper 取代）。用 `@functools.wraps` 修正：

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # 保留原函式的名稱和 docstring
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """跟某人打招呼"""
    return f"Hello, {name}"

print(greet.__name__)  # "greet"（沒有 @wraps 的話會是 "wrapper"）
print(greet.__doc__)   # "跟某人打招呼"
```

---

### 實際常用的 Decorator 範例

```python
from functools import wraps

# 1. 日誌記錄（Logging）
def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"呼叫 {func.__name__}，參數: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} 回傳: {result}")
        return result
    return wrapper

@log
def add(a, b):
    return a + b

add(3, 5)
# 呼叫 add，參數: args=(3, 5), kwargs={}
# add 回傳: 8

# 2. 權限檢查
def require_admin(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if user.get("role") != "admin":
            raise PermissionError("需要管理員權限")
        return func(user, *args, **kwargs)
    return wrapper

@require_admin
def delete_user(current_user, user_id):
    print(f"刪除使用者 {user_id}")

admin = {"name": "Alice", "role": "admin"}
normal = {"name": "Bob", "role": "user"}

delete_user(admin, 123)   # 正常執行
# delete_user(normal, 123)  # 拋出 PermissionError

# 3. 快取 / Memoization
def cache(func):
    """快取函式結果，相同參數不重複計算"""
    memo = {}
    @wraps(func)
    def wrapper(*args):
        if args not in memo:
            memo[args] = func(*args)
        return memo[args]
    return wrapper

@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(50))  # 12586269025（瞬間算完，沒有重複計算）

# Python 內建也有：
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

---

### Class-based Decorator

除了用函式，也可以用 class 來寫 decorator：

```python
class CountCalls:
    """記錄函式被呼叫幾次"""
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} 已被呼叫 {self.count} 次")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")

say_hello()  # say_hello 已被呼叫 1 次 → Hello!
say_hello()  # say_hello 已被呼叫 2 次 → Hello!
say_hello()  # say_hello 已被呼叫 3 次 → Hello!
```

---

### 在 FastAPI 裡的 Decorator

FastAPI 的路由本身就是 decorator：

```python
from fastapi import FastAPI, Request
from functools import wraps

app = FastAPI()

# FastAPI 的 @app.get() 就是 decorator
@app.get("/")
async def root():
    return {"message": "Hello World"}

# 自訂 decorator 用在 FastAPI 路由上
def rate_limit(max_calls=10):
    """簡易版流量限制 decorator"""
    calls = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            calls[client_ip] = calls.get(client_ip, 0) + 1
            if calls[client_ip] > max_calls:
                return {"error": "Too many requests"}
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

### Decorator 重點整理

| 概念 | 說明 |
|------|------|
| 用途 | 在不改動原函式的情況下新增功能 |
| 語法 | `@decorator` 放在函式定義上方 |
| 本質 | `fn = decorator(fn)` 的語法糖 |
| `@wraps` | 保留原函式的 `__name__` 和 `__doc__` |
| 帶參數 | 多包一層函式：`@decorator(arg)` |
| 常見用途 | logging、計時、快取、權限檢查、重試 |
| 內建好用的 | `@property`、`@staticmethod`、`@classmethod`、`@lru_cache` |
