# IOT公司爬虫
## crawler
python3 爬虫脚本
脚本的说明，需要依赖的库请清参见爬虫文档.docx  
## frontend 
操作脚本与搜索使用的前端  
前段的部署与数据库的部署也请参考爬虫文档.docx  
使用前段操作脚本的功能需要将脚本放到/cawler文件夹中，或者修改php中的脚本位置  
## iot_docker.tar
由于配置脚本需要安装一些库，配置数据库和前段等操作中很容易因为编码或文件位置错误造成无法正常运行，故准备此docker镜像来提供配置参考  
脚本位置/crawler中，前段位于/var/www/html中，数据库root密码为misakaxindex  
使用`docker load iot_docker.tar`导入image  
之后使用`docker run -it -p 8080:80 iot_docker`来运行镜像，加入-it参数和-p 80:80来显示shell与映射http端口  
进入系统后使用`service apache2 start`和`service mysql start`来启动apache与mysql 
(在windows上mysql启动失败需要先执行`chown -R mysql:mysql /var/lib/mysql /var/run/mysqld`)  
之后访问localhost:80就可以正常访问前端  

注：因为docker镜像比较大(1.3g)，故使用code_only分支只存放代码  

