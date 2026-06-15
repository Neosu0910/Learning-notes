# 定義生成器函式
def test():
    print ("階段一")
    yield 3
    print ("階段二")
    yield 10
#呼叫並回傳生成器
gen=test()

#搭配for迴圈中使用
for d in gen:
    print(d) 