from http.server import BaseHTTPRequestHandler,HTTPServer
import sys,os
import subprocess


#-------------------------------------------------------------------------------------
class ServerException(Exception):
    '''For Server internal error reproting.'''
    pass

#-------------------------------------------------------------------------------------------
class Base_case(object):
    '''base case'''
    def handle_file(self,handler,full_path):
        try:
            with open(full_path,'rb') as reader:
                content=reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg="'{0}'cannot be read:{1}".format(self.path,msg)
            self.handle_error(msg)

    def index_path(self,handler):
        return os.path.join(handler.full_path,"index.html")

    def test(self,handler):
        assert False,'Not implemented.'

    def act(self,handler):
        assert False,'Not implemented.'


#-----------------------------------------------------------------------------
class Case_no_file(Base_case):
    '''file is not exists'''
    def test(self,handler):
        return not os.path.exists(handler.full_path)

    def act(self,handler):
        raise ServerException("'{0}'not found".format(handler.path))

#-----------------------------------------------------------------------------
class Case_cgi_file(Base_case):
    '''Executable script'''
    def run_cgi(self,handler):
        data=subprocess.check_output(["python",handler.full_path])
        handler.send_content(data)

    def test(self,handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self,handler):
        self.run_cgi(handler)

#-----------------------------------------------------------------------------

class Case_existing_file(Base_case):
    '''file exist'''
    def test(self,handler):
        return os.path.isfile(handler.full_path)

    def act(self,handler):
        self.handle_file(handler,handler.full_path)

#-----------------------------------------------------------------------------

class Case_directory_index_file(Base_case):
    '''return homepagefile in the root path'''
    def test(self,handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self,handler):
        self.handle_file(handler,self.index_path(handler))

#------------------------------------------------------------------------------
class Case_always_fail(Base_case):

    '''Base case if nothing else worked'''
    def test(self,handler):
        return True

    def act(self,handler):
        raise ServerException("Unknown object'{0}'".format(handler.path))

#------------------------------------------------------------------------------    
class RequestHandler(BaseHTTPRequestHandler):
    '''
    If the requested path maps to a file,that file is served.
    If anything goes wrong, an error page is constructed.
    '''
    Cases=[Case_no_file(),
           Case_cgi_file(),
           Case_existing_file(),
           Case_directory_index_file(),
           Case_always_fail()]

   #Error Page
    Error_Page="""\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def do_GET(self):
        try:
            #Get full path
            self.full_path=os.getcwd()+self.path

            #Traverse all the cases

            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

        #Handle error
        except Exception as msg:
            self.handle_error(msg)

    def handle_error(self,msg):
        content=self.Error_Page.format(path=self.path,msg=msg)
        self.send_content(content,404)

    #Send the data th client

    def send_content(self,content,status=200):
        self.send_response(status)
        self.send_header("Content-type","text/html")
        self.send_header("Content-length",str(len(content)))
        self.end_headers()
        self.wfile.write(content)

#-----------------------------------------------------------------------

if __name__=='__main__':
    serverAddress=('',8080)
    server=HTTPServer(serverAddress,RequestHandler)
    server.serve_forever()
