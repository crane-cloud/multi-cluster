from jsonrpcserver import serve, method, serve,  Success, Result, Error
import os

host = os.getenv('HOST', 'localhost')
port = os.getenv('TEST_PORT', 5100)

def main():
    print('Welcome to the cluster-peer-app')

if __name__ == "__main__":
    main()
    serve(host, 5100)
