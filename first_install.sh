#!/bin/bash
if [ -d env ];then
    cd env
    echo "进入env文件夹"
    else
    mkdir env
    cd env
    echo "env文件夹不存在"
fi
if [ -d CCP_OA ];then
    echo "python虚拟环境已存在"
    source CCP_OA/bin/activate
    else
    echo "开始创建python虚拟环境"
    virtualenv CCP_OA --python=python3
    source CCP_OA/bin/activate
    pip install django
fi
cd ..

if [ -d static/photo ];then
    echo "存放头像的文件夹存在"
    else
    mkdir static/photo
    echo "创建photo文件夹成功"
fi
sudo chmod 777 static/photo

find . -path "*/activity/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/journey/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/main_site/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/user_info/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*.pyc"  -delete
if [ -f db.sqlite3 ];then
    rm db.sqlite3
fi
python manage.py makemigrations
python manage.py migrate
python manage.py install
chmod 777 db.sqlite3
sudo systemctl restart apache2