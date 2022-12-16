from jsonrpcserver import serve
import os


def main():
    print('hey')


host = os.getenv('HOST', 'localhost')
port = os.getenv('TEST_PORT', 5100)
if __name__ == "__main__":
    main()
    serve(host, 5100)
