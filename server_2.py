from http.server import BaseHTTPRequestHandler,HTTPServer
import sys,os


class ServerException(Exception):
    """服务器内部错误"""
    pass


class case_no_file(object):
    '''该路径不存在'''

    def test(self,handler):
        return not os.path.exists(handler.full_path)

    def act(self,handler):
        raise ServerException("'{0}'not found".format(handler.path))

class case_existing_file(object):
    '''该路径是文件'''
    def test(self,handler):
        return os.path.isfile(handler.full_path)

    def act(self,handler):
        handler.handle_file(handler.full_path)

class case_always_fail(object):
    '''所有情况都不符合时候的默认处理类'''
    def test(self,handler):
        return True

    def act(self,handler):
        raise ServerException("Unkown object '{0}'".format(handler.path))

class case_directory_index_file(object):

    def index_path(self,handler):
        
        return os.path.join(handler.full_path,'test1.html')
        
    #判断目标路径是否是目录&&目录下是否有index.html

    def test(self,handler):
       
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    #响应index.html的内容
    def act(self,handler):
        
        handler.handle_file(self.index_path(handler))
    

class RequestHandler(BaseHTTPRequestHandler):
    """
    处理请求并返回页面
    """
    #所有可能情况
    Cases=[case_no_file(),
           case_existing_file(),
           case_directory_index_file(),
           case_always_fail()]
    
   
    #处理一个GET请求
    def do_GET(self):
        try:
            #文件完整路径
            self.full_path=os.getcwd()+self.path
            print(self.full_path)

           #遍历所有可能的情况
            for case in self.Cases:
               #如果满足该类情况
               if case.test(self):
                   #调用相应的act函数
                   case.act(self)
                   break
        #处理异常
        except Exception as msg:
            self.handle_error(msg)

            

    def handle_file(self,full_path):
        try:
            
            with open(full_path,'rb') as reader:
                
                content=reader.read()
                
            self.send_content(content)
        except IOError as msg:
            msg="'{0}'cannot be read:{1}".format(self.path,msg)
            self.handle_error(msg)

    Error_Page="""\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """
    def handle_error(self,msg):
        content=self.Error_Page.format(path=self.path,msg=msg)
        self.send_content(content,404)


    def send_content(self,content,status=200):
        #...待实现...#
        self.send_response(status)
        self.send_header("Content-type","text/html")
        self.send_header("Content-Length",str(len(content)))
        self.end_headers()
        self.wfile.write(content)





if __name__=='__main__':
    serverAddress=('',8080)
    server=HTTPServer(serverAddress,RequestHandler)
    server.serve_forever()
