#判斷式
# if False:
#     print("True 執行")
# else:
#     print("Flase 執行")

# x=input("請輸入數字")
# x=int(x)
# if x>200:
#     print("大於100")
# elif x>100:
#     print("大於100,小於等於200")
# else:
#     print("小於等於 100")

n1= int(input("請輸入數字1: "))
n2= int(input("請輸入數字2: "))
op= input("請輸入:+,-,*,/: ")
if op=="+":
    print(n1+n2)
elif op== "-":
    print(n1-n2)
elif op== "*":
    print(n1*n2)
elif op== "/":
    print(n1/n2)
else :
    print("超出範圍")    