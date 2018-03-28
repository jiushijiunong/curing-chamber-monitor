# curing chamber monitor

## Build & Test Status
* [![Build Status](https://travis-ci.org/littlepiggroup/curing-chamber-monitor.svg?branch=integration)](https://travis-ci.org/littlepiggroup/curing-chamber-monitor)

## 项目结构
* curing chamber monitor目录是Django的project, ccm/ccmdb是Django的app. 一个project可以包含多个app.
* http://www.django-rest-framework.org/tutorial/quickstart/ it explains why place db folder under pocket-monitor.
`It may look unusual that the application has been created within the project directory. Using the project's namespace avoids name clashes with external module (topic goes outside the scope of the quickstart).`
* In best practice, we don't place app folder under site-level folder: https://docs.djangoproject.com/en/1.11/intro/tutorial01/#creating-a-project,
https://www.revsys.com/blog/2014/nov/21/recommended-django-project-layout/

## Code flow:
### urls -> db.urls -> db.views -> db.serializers -> db.models
1. urls: expose urls
2. db.urls: define the exposed rest apis
3. db.views: define the views mapping to the exposed rest apis
4. db.serializers -> serialize/deserialize model between views and backend models
5. db.models -> backend models associated to db tables.

## Set up
Install depends libs
```shell
pip install django
pip install djangorestframework
pip install django-filter
```

Install\Upgrade db

```shell
python install_db.py
```

## Start server

```shell
python start.py
```

## End to end test
Use restful client browser plugin or install command line tool restful client as below:
```shell
pip install httpie
```
Reference: Command Line Restful Client <https://httpie.org/doc>

## Browse db tables

```shell
pip install sqlite-web
python admin.py
```
Reference: Sqlite DB Browser <https://github.com/coleifer/sqlite-web>

## Tips
add super user
```shell
python manage.py createsuperuser --username=admin --email=admin@example.com
```
