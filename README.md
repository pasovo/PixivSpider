**一个Pixiv小爬虫，支持长时间爬取 跳过已经爬过的 支持R18**

修改于https://github.com/nyaasuki/PixivSpider

原项目也可以使用，我基于源代码添加了R18，修改数据库为sqlite，感谢大佬的代码


## 环境需求

Python:3.6+

## 食用方法

**Linux/OSX:**
1. 
```shell
git clone https://github.com/nyaasuki/PixivSpider.git && cd ./PixivSpider
```
2. 修改配置文件config.ini,配置文件内有说明
3. 
```shell
python3 Pixiv.py
```

**Windows:**

1. 下载/clone这个项目

2. 修改配置文件config.ini,配置文件内有说明

2. 配置好环境（python）

3. 打开你的CMD窗口

4. 输入python+‘ ’    ←这是一个空格

5. 用鼠标把**Pixiv.py**这个文件拖到cmd窗口

   ​	^_^

## 注意事项

1.requests安装错误

`ERROR: Could not find a version that satisfies the requirement resquests
ERROR: No matching distribution found for resquests`

解决方案：手动安装requests

'pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests'

2.请输入一个cookie

~~目前此项留空直接回车也可以正常爬取，如果后续添加新功能可以能需要~~ 爬R18需要cookie，你懂的

### cookie获取帮助
```
1.  首先打开你的电脑浏览器(此处以Microsoft Edge为例)

2.  进入你的Pixiv主页，点击关注按钮查看关注的用户。
    此时你浏览器上方地址栏的地址应该是这样的
        https://www.pixiv.net/users/你的用户ID/following
    或这样的
        https://www.pixiv.net/users/你的用户ID/following?p=数字

3.  按压并释放你键盘上的F12功能键(它一般在键盘的第一排最后几个)
    或是按照下面的步骤来
        点击浏览器右上角的三个点 -> 更多工具 -> 开发人员工具
    如果窗口跳出来了之后没有中文(你看不懂英文的话)
        点击窗口右上角的设置图标 -> Language -> 中文简体

4.  关掉设置，返回开发人员工具主页面，点击菜单栏中的”网络“
    在”保留日志“与”禁用缓存“那一栏的下方找到下面这一栏内容
        全部 Fetch/XHR JS CSS img 媒体....
    然后勾选"Fetch/XHR"

5.  按住你键盘上的Ctrl键(它一般在键盘最左下角)，并按R键。
    松开所有按键，此时浏览器页面会刷新，并在”开发人员工具“的
    页面窗口中多出几条数据。

    找到名称前部为"following?offset=数字&limit=24"的那一条数据
    用鼠标左键点击它，查看内容。

6.  在跳出的侧边窗口中往下滑动鼠标滚轮，在请求标头找到cookie那一项
    鼠标右键点击它”复制值“

    再将它保存在某个文件中，这样你就拥有自己的Cookie数据了(不过请注意
    不要泄露给他人)
```

此项储存在本地cookie.txt文件中，失效了可以删除重新填入

## 特别提醒

正常来说，当没有出现上方问题时，程序出现问题大多为你的上网方式不够科学
缓慢更新中...

