# 基于Django实现的可重用登录注册系统
## 简单的使用方法
1. 使用pip安装第三方依赖包 
2. 修改settings.example.py变为settings.py，
并填写邮件发送端的用户和密码
3. 运行python manage.py migrations & migrate命令，
创建数据库和数据表，默认使用的是sqlite，如果使用MySQL，请
用户自己修改settings.py配置
4. 运行python run server 0.0.0.0:8000 启动服务器

## 路由设置
```python
from django.contrib import admin
from django.urls import path, include
from login import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('confirm/', views.user_confirm),
    path('captcha/', include('captcha.urls'))   # 增加这一行
]
```
