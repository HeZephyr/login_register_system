from django.db import models


# Create your models here.

class User(models.Model):
    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    # 通过选择列表来确定值
    sex = models.CharField(max_length=32, choices=gender, default="男")
    create_time = models.DateTimeField(auto_now_add=True)
    has_confirmed_email = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        # 指定排序方式，按创建时间来排序，最近的最先显示，加了-为降序排列，不加为升序排列
        ordering = ["-create_time"]
        # 用于设置模型对象的直观、人类可读的名称，可以用中文
        verbose_name = "用户"
        # 复数名，即复数的时候使用的名称
        verbose_name_plural = "用户"


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('user', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + " " + self.code

    class Meta:
        ordering = ["-create_time"]
        verbose_name_plural = "确认码"
        verbose_name_plural = "确认码"
