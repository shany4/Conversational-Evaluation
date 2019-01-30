# 安装Apache 和 mod_wsgi

`sudo apt-get install apache2`


`sudo apt-get install libapache2-mod-wsgi`

检查是否安装成功：


`apachectl -v`

# 在$HOME下安装Django和所需的module：
`sudo -H pip install Django==1.11`


（以及其他项目里依赖的module，例如annotation——system里要
`sudo -H pip install xlrd` ， `sudo -H pip install django-excel` 等）

（一定要加`-H` tag，把Django和其他module装在HOME下，要不apache找不到安装的django）

# 把project git clone下来
先试着跑一下：

`python manage.py collectstatic`

`python manage.py runserver`

# 修改Apache的配置文件
ubuntu的apache2配置文件在 `/etc/apache2/` 下：

一般在000-default.conf文件下修改就行，不过也可以为每一个项目新建一个.conf文件

`sudo vi /etc/apache2/sites-available/000-default.conf`

然后在文件里添加以下highlighted部分（其余为文件里本来就有的）：

    <VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com
 
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
 
        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn
 
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
 
        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
```diff
+       Alias /media/ /home/tyzhou/annotation/media/
        
+       Alias /static/ /home/tyzhou/annotation/common_static/
 
+       <Directory /home/tyzhou/annotation/media/>
+                Require all granted
+       </Directory>
 
+       <Directory /home/tyzhou/annotation/common_static/>
+                Require all granted
+       </Directory>
 
+       WSGIScriptAlias / /home/tyzhou/annotation/annotation/wsgi.py
 
+       <Directory /home/tyzhou/annotation/annotation/>
+               <Files wsgi.py>
+                       Require all granted
+               </Files>
+       </Directory>
```
 
    </VirtualHost>

将以上文件夹路径更换为要部署的project的media/common_static文件夹或wsgi.py文件路径


# 修改project的wsgi.py文件:

    import os
    import sys
    from os.path import join, dirname, abspath
    from django.core.wsgi import get_wsgi_application
 
    PROJECT_DIR = dirname(dirname(abspath(__file__)))
 
    sys.path.insert(0, PROJECT_DIR)
 
    os.environ["DJANGO_SETTINGS_MODULE"] = "annotation.settings" 
 
    application = get_wsgi_application()


# 设置目录和文件权限:

- 一般目录权限设置为 755，文件权限设置为 644 


### 1.假如项目位置在 /home/user/projectName （manage.py文件在projectName文件夹下）:

`cd /home/user/`

`sudo chmod -R 644 projectName`

`sudo find projectName -type d | xargs chmod 755`


### 2.设置media文件夹权限：
假如上传目录为 /home/user/projectName/media/uploads 文件夹,进入media文件夹，将 uploads 用户组改为www-data，并且赋予该组写权限:

`cd media/ # 进入media文件夹`

`sudo chgrp -R www-data uploads`

`sudo chmod -R g+w uploads`


### 3.设置sqlite3数据库权限：
同样要给www-data写数据库的权限，假设db.sqlite3文件在/home/user/projectName下，进入/home/user执行下列操作：

`cd /home/user`

`sudo chgrp www-data projectName`

`sudo chmod g+w projectName`

`sudo chgrp www-data projectName/db.sqlite3`

`sudo chmod g+w projectName/db.sqlite3`

# Q&A：

+ Q：如果网站打开后Internal Server Error 500：

> A：可以sudo cat /var/log/apache2/error.log来查看error log



+ Q：更改project代码后或apache配置文件后网页没有更新

> A：重启Apache Server：sudo service apache2 restart
