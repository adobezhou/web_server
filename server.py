from http.server import BaseHTTPRequestHandler,HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    """
    处理请求并返回页面
    """
    #页面模板
    Page="""\
        <html>
        <body>
        <p>Hello,Web!</p>
        </body>
        </html>
        """
    #处理一个GET请求
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.send_header("Content-Length",str(len(self.Page)))
        self.end_headers()
        self.wfile.write(self.Page.encode())


if __name__=='__main__':
    serverAddress=('',8080)
    server=HTTPServer(serverAddress,RequestHandler)
    server.serve_forever()
