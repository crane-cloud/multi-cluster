from jsonrpcserver import serve, method, serve,  Success, Result, Error
import os

@method
def peer_message_response(url) -> Result:
    print('from:', url)
    current_port =  int(os.getenv('PORT'))
    return Success({"data":"null", "current": current_port, "url": url})

host = os.getenv('HOST', 'localhost')
port = os.getenv('TEST_PORT', 5100)

def main():
    print('Welcome to the cluster peer app')

if __name__ == "__main__":
    main()
    serve(host, 5100)
