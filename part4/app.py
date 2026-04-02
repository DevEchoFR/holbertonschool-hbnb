def application(environ, start_response):
    """
    A simple WSGI application for demonstration.
    Serves static files from the 'part4' directory and returns index.html for root.
    """
    import os
    from urllib.parse import unquote

    root_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(root_dir, 'static')
    path = unquote(environ.get('PATH_INFO', '/'))
    if path == '/':
        file_path = os.path.join(root_dir, 'index.html')
    elif path.startswith('/static/'):
        file_path = os.path.join(root_dir, path.lstrip('/'))
    else:
        file_path = os.path.join(root_dir, path.lstrip('/'))
        if not os.path.isfile(file_path):
            file_path = os.path.join(root_dir, 'index.html')

    if os.path.isfile(file_path):
        if file_path.endswith('.html'):
            content_type = 'text/html'
        elif file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.png'):
            content_type = 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif file_path.endswith('.ico'):
            content_type = 'image/x-icon'
        else:
            content_type = 'application/octet-stream'
        with open(file_path, 'rb') as f:
            content = f.read()
        start_response('200 OK', [('Content-Type', content_type)])
        return [content]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'404 Not Found']


# Add WSGI server startup for direct execution
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = 8000
    host = '0.0.0.0'
    print(f"Serving on http://{host}:{port}")
    with make_server(host, port, application) as httpd:
        httpd.serve_forever()
