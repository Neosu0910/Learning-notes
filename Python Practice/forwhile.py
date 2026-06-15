#while 迴圈
n=1
sum=0 #數字加總
while n<=10:
    sum=sum+n
    n +=1
print(sum)

#for迴圈
for x in range(5,10):
    print(x)

#for 1+到 10
sum=0
for x in range(1,11):
    sum=sum+x #sum+=sum
print(sum)

#break 簡易範例
n=0
while n<5:
    if n==3:
        break
    print(n)
    n+=1
print("最後的n: ",n)
#continue 簡易範例

n=0
for x in [0,1,2,3]:
    if x%2==0:
        continue
    print(x)
    n+=1
print(n)

#else 簡易範例
sum=0
for n in range(11):
    sum+=n
else:
    print(sum)

# 綜合範例: 找出整數平方根
# n=1
# while n<5:
#     print("變數n的資料是:",n)
#     n+=1
# else:   
#     print(n)