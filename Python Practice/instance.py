#Point 實體物件的設計: 平面座標上的點
# class Point:
#     def __init__(self,x,y):
#         self.x=x
#         self.y=y
# #建立第一個實體物件
# p1=Point(3,4)
# print(p1.x,p1.y)

# #建立第二個實體物件
# p2=Point(4,7)
# print(p2.x,p2.y)


# Fullname 實體物件的設計：分開記錄姓,名資料的全名
# class Fullname:
#     def __init__(self,first,last):
#         self.first=first
#         self.last=last
# name1=Fullname("Su","Cheng Hao")
# print(name1.first,name1.last)

##Point 實體物件的設計 平面座標上的點
class Point:
    def __init__(self,x,y):
        self.x=x
        self.y=y
    #定義實體方法
    def show(self):
        print(self.x,self.y)
    def distance(self,targetX,targetY):
        return(((self.x-targetX)**2)+((self.y-targetY)**2))**0.5
p=Point(3,4)
p.show() #呼叫實體方法/函式
result=p.distance(0,0)
print(result)


