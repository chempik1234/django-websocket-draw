## Django realtime drawing with websockets
### What is this?
This is a simple test project that I made to learn django websockets (`djangochannelsrestframework`)
### What's inside?
It contains a single django application called _drawing_ and simple setup instructions.

There are no static/media files, because I wanted this app to be light and wrote some simple HTML templates with scripts right inside them.
### Setup
If you don't know how to quickly start a redis server, visit `ubuntu redis commands.txt`:
```commandline
sudo apt-add-repository ppa:redislabs/redis
sudo apt-get install redis-server -y
sudo service redis-server restart
```

Firstly, **change your current directory** to *realtime_drawing_django*

Use `pip install -r requirements.txt` to install all the dependencies.

Since migrations are in .gitignore, make them yourself by using:
```commandline
python manage.py makemigrations
python manage.py migrate
```

If you don't know how to quickly start a daphne server (which I used here), visit `daphne start command.txt`:
```commandline
daphne realtime_drawing_django.asgi:application
```