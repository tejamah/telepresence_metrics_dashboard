from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

if __name__ == "__main__":
    dist_dir = Path(__file__).resolve().parent / "dist"
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(  # noqa: E731
        *args,
        directory=str(dist_dir),
        **kwargs,
    )
    server = ThreadingHTTPServer(("127.0.0.1", 5180), handler)
    server.serve_forever()
