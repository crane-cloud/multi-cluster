from server import create_app

app = create_app('production')

if __name__ == '__main__':
    app.run()

# Run this file using;
#    gunicorn --bind 0.0.0.0:5000 wsgi:app
#    gunicorn wsgi:app
