'''
Just a little prototype server
'''
import ssl, http.server, json, pprint

__decrast_server_version__= "0.1"

# define a custom request handler for our de-crast server
class decrast_handler(http.server.BaseHTTPRequestHandler) :

    # The server software version. This gets added into all response headers
    server_version = "decrast_api/" + __decrast_server_version__
    
    def do_GET(self) :
        """
        The server might not even support get requests. I makes sense to me to
        just handle all server requests through POST requests.
        """
        print("I just got a GET request")
        
        # This is just some garbage return value for now
        out_data = {"code" : "400",
                    "description" : "GET request are not supported"}

        # send back a big fuck you.
        self.respond_with_json(out_data)

    def do_POST(self) :
        """
        The server will mostly if not only handle POST requests
        """
        print("I just got a POST request\n")
        
        # print the header (debugging)
        print(self.headers.as_string())

        # retrieve the json object
        in_data = self.dump_json()

        # json objects represent an action the server needs to take. So, process
        # the request. This is where the majority of the server logic will take
        # place. This call will construct a new json object that will contain
        # all necessary information that the client wanted. or a json object 
        # representing an error appropriate to what got fucked up.
        out_data = self.process_json(in_data)

        # respond to the http request with the response json object 
        self.respond_with_json(out_data)

        # print the inbound and outbound json objects (debugging)
        pp = pprint.PrettyPrinter()
        print("\nInbound JSON:\n")
        pp.pprint(in_data)
        print("\nOutbound JSON:\n")
        pp.pprint(out_data)

    def send_json_header(self, json_bytes) :
        """
        writes a header for a json object response
        """
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(json_bytes)))

    def dump_json(self) :
        """
        TODO(Jeremy): this should check if the packet contains json or not
        """
        # get the size of the json object from the headers. If there is no 
        # Content-Length header self.headers.get() will return None, and 
        # int(None) throws a TypeError
        try :
            in_data_len = int(self.headers.get("Content-Length"))
        except TypeError :
            return {"code" : "400",
                    "client-error" : "no 'Content-Length' header"}

        # read the data from the requests data buffer into a bytes object
        in_data = self.rfile.read(in_data_len)
        
        # convert the bytes object into a python dict/list blob. If the data
        # is not a valid json object this will throw an error.
        try :
            in_data = json.loads(in_data)
        except json.decoder.JsonDecodeError :
            return {"code" : "400",
                    "client-error" : "bad JSON"}

        return in_data

    def process_json(self, in_data) :
        """
        does the majority of the server logic, and constructs a response json
        object to return. Every return json should have a "code" field. This
        code should be the http status code. that will simplify the header 
        creation logic the server needs to do.

        Some codes we should probably use:
            Success codes:
                200 : OK
                201 : Created - The request has been fulfilled, resulting in the 
                                creation of a new resource.
            
            Client error codes:
                400 : Bad Request
                401 : Unauthorized
                403 : Forbidden
            
            Server error codes:
                500 : Internal Server Error
                501 : Not Implemented

        """
        # if the json has a 'client-error' field then it is an internal error
        # json so return it so it can be sent back to the user
        try :
            in_data["client-error"]
            return in_data
        except KeyError :
            pass

        return {"code" : "501",
                "discription" : "The programmer who made this " 
                                "must be super lazy or something."
               }

    def respond_with_json(self, out_data) :
        """
        takes a "json" object (really a dict/list blob) and sends it back to the
        client with the appropriate headers and stuff.
        """
        # send the http status code
        status_code = int(out_data["code"])
        self.send_response(status_code)
    
        # turn the python dict/list blob back into json bytes
        json_bytes = json.dumps(out_data, indent=2).encode("utf-8")
        json_bytes += b"\n"

        # send the header
        self.send_json_header(json_bytes)
        self.end_headers()

        # write out the json bytes
        self.wfile.write(json_bytes)

        return json_bytes

    def version_string(self):
        """Return the server software version string."""
        """
        This overrides the default version string call. otherwise it sends 
        the python version we are using and the class we are overriding. that
        just seems like to much info to give every client.
        """
        return self.server_version

        



def setup_server(hostname="localhost", port=4443, 
                 cacert="cert.pem", privkey="privkey.pem") :
    # parameters
    server_addr = (hostname, port)

    # create an http server with our custom handler function
    httpd = http.server.HTTPServer(server_addr, decrast_handler)

    # wrap the server's socket in the ssl context that we created
    #httpd.socket = ssl.wrap_socket(httpd.socket, 
    #                               server_side=True,
    #                               certfile=cacert,
    #                               keyfile=privkey)
    
    # return the new server
    return httpd

if __name__ == "__main__" :
    httpd = setup_server()

    print("you just got served...\n")

    # serve forever
    #httpd.serve_forever()
    
    ## serve one request and exit. (for debugging)
    httpd.handle_request()

