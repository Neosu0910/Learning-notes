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
