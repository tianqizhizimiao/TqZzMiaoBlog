# app.py
"""调试用静态页路由：把 public/ 文件夹按路径规则映射为 URL，并限速模拟真实加载环境。

路径规则：
    public/index.html       ->  /
    public/xxx.html         ->  /xxx.html
    public/testdir/xxx.html ->  /testdir/xxx.html

上线时把 public/ 整个文件夹静态托管（如 GitHub Pages），不再需要 Flask。
"""
import os
import time

from flask import Flask, send_from_directory, abort, redirect

app = Flask(__name__)

# 静态页面根目录（相对本文件）。想改名只改这一行。
PAGES_DIR = os.path.join(os.path.dirname(__file__), "public")

# 限速：默认 50 KB/s = 50 * 1024 B/s = 51200 B/s（极慢，模拟极端环境）。
# 也可用环境变量 RATE_KBPS 覆盖（单位 KB/s），如 RATE_KBPS=200 python app.py。
# 想改速率可以直接改这一行，或用环境变量。
RATE_BYTES_PER_SEC = int(os.environ.get("RATE_KBPS", "50")) * 1024


class ThrottleMiddleware:
    """WSGI 中间件：把每个响应的字节流限速到指定速率（bytes/s），模拟真实下载带宽。

    每个连接（请求）独立计时、独立限速，更接近真实的多用户加载环境。
    """

    def __init__(self, app, bytes_per_sec):
        self.app = app
        self.bytes_per_sec = bytes_per_sec

    def __call__(self, environ, start_response):
        body = self.app(environ, start_response)
        return self._throttle(body)

    def _throttle(self, body):
        start = time.monotonic()
        sent = 0
        try:
            for chunk in body:
                sent += len(chunk)
                # 期望耗时 = 已发送字节 / 速率
                expected = sent / self.bytes_per_sec
                elapsed = time.monotonic() - start
                if expected > elapsed:
                    time.sleep(expected - elapsed)
                yield chunk
        finally:
            # 释放底层响应体（例如文件句柄）
            close = getattr(body, "close", None)
            if close is not None:
                close()


# 用限速中间件包裹整个 WSGI 应用，所有响应都会经过它
app.wsgi_app = ThrottleMiddleware(app.wsgi_app, RATE_BYTES_PER_SEC)


class DelayMiddleware:
    """WSGI 中间件：每个请求在响应前额外延迟指定的毫秒数，模拟网络往返。

    用环境变量 DELAY_MS 控制（单位毫秒），默认 500ms。
    """

    def __init__(self, app, delay_ms):
        self.app = app
        self.delay_s = delay_ms / 1000.0

    def __call__(self, environ, start_response):
        if self.delay_s > 0:
            time.sleep(self.delay_s)
        return self.app(environ, start_response)


# 延迟中间件在外层，限速在最内层：先延迟、再限速，模拟真实网络
app.wsgi_app = DelayMiddleware(
    app.wsgi_app, int(os.environ.get("DELAY_MS", "500"))
)


@app.after_request
def no_cache(resp):
    """开发环境禁用缓存：每次刷新都重新加载资源（不走 304/浏览器缓存）。

    去掉 ETag / Last-Modified 可条件验证头，并强制 no-store。
    这样配合限速，每次刷新都能完整经历慢速加载。
    """
    resp.headers["Cache-Control"] = "no-store, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers.pop("ETag", None)
    resp.headers.pop("Last-Modified", None)
    return resp


@app.route("/")
def index():
    return send_from_directory(PAGES_DIR, "index.html")


@app.route("/<path:subpath>")
def page(subpath):
    # 1) 普通文件：/xxx.html -> public/xxx.html
    if os.path.isfile(os.path.join(PAGES_DIR, subpath)):
        return send_from_directory(PAGES_DIR, subpath)

    # 2) 目录：/testdir/ -> public/testdir/index.html；无尾斜杠的 /testdir 统一重定向
    dir_index = os.path.join(PAGES_DIR, subpath, "index.html")
    if os.path.isfile(dir_index):
        if not subpath.endswith("/"):
            return redirect("/" + subpath + "/")
        return send_from_directory(PAGES_DIR, os.path.join(subpath, "index.html"))

    # 3) 没有命中 -> 交给 Flask 默认 404
    abort(404)


if __name__ == "__main__":
    # 监听 0.0.0.0：对局域网开放（同一局域网设备可通过本机 IP 访问）。
    # 可用环境变量 HOST 覆盖，如 HOST=127.0.0.1 python app.py（仅本机）。
    host = os.environ.get("HOST", "0.0.0.0")
    # threaded=True：多连接并发，每条连接各自限速
    app.run(host=host, port=5000, debug=True, threaded=True)
