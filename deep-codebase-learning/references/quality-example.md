# 完整功能主课：浏览器打开 `/plain.html`，服务器如何识别请求、读取文件并返回页面

> **当前完整功能主课。** 本课沿一条完整路径：浏览器发出 `GET /plain.html`，Python 标准库解析请求并调用项目处理器，处理器从进程当前目录找到 `plain.html`，读出文件字节（每个字节由 8 个二进制位组成），组装 HTTP 响应，浏览器再把响应正文解释为 HTML。下方原有的 Markdown 标题检查课保留为历史局部读码参照，不能用它的篇幅或范围校准完整功能课。
>
> **源码与证据范围。** 项目源码固定为 [aosabook/500lines 提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2` 的 `web-server/code/03-handlers/server.py` 原行 1–108](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L1-L108) 和同目录 [`plain.html` 原行 1–9](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/plain.html#L1-L9)。行号来自固定提交的原始文件字节和 LF 换行，不来自网页抽取后的显示行号。机制依据是 CPython 2.7.18 的 `BaseHTTPServer.py`、`SocketServer.py` 与该版本标准库文档；HTTP/1.1 的消息边界只用 RFC 9112 说明通用格式。源码是 Python 2 时代的示例，本文不把它改写成 Python 3，也没有启动服务或打开浏览器；运行命令只作可选操作说明。

## 1. 业务场景与本课目标

### 访问本机页面为什么需要服务器

你有一个写着网页标题和正文的文件（HTML 文件），双击它可以让本机浏览器直接从磁盘打开。这个动作不会向 Python 程序发送 HTTP（Hypertext Transfer Protocol，超文本传输协议）请求；HTTP 是浏览器与服务程序约定请求、响应结构的规则。若希望浏览器用 `http://...` 地址访问文件，就需要一个正在运行的服务程序：它在端口等待连接，收到请求后替浏览器读磁盘，再把结果写回网络。我们沿最小场景追踪这件事：浏览器访问同一台机器上的 `plain.html`。

### 这条 URL 带着哪些现场值

本例地址是 `http://127.0.0.1:8080/plain.html`。URL（Uniform Resource Locator，统一资源定位符）把访问方案、主机、端口和目标放在一个地址里：`http` 选择 HTTP（Hypertext Transfer Protocol，超文本传输协议），`127.0.0.1` 是本机回环 IPv4（Internet Protocol version 4，互联网协议第 4 版）地址，`8080` 是端口，`/plain.html` 是请求目标。HTTP 规定请求与响应的消息结构；TCP（Transmission Control Protocol，传输控制协议）负责把两端之间的字节送到连接上。IP（Internet Protocol，互联网协议）负责网络寻址，端口让操作系统把到达的连接交给监听该端口的程序。程序通过 socket（套接字）读写网络连接；socket 是网络 I/O（Input/Output，输入/输出）接口，不是磁盘文件。

这里浏览器请求 `GET /plain.html`，服务器按文件规则查找目标并回送页面内容。

浏览器和服务器是两个程序角色；远端部署时它们的文件系统也可能位于不同机器。本例的 `127.0.0.1` 把客户端连接指回本机，但浏览器仍不会因为 URL 中出现了 `plain.html` 就直接读取服务器进程当前目录里的文件。它向服务器发请求，由服务器进程访问文件，再把内容写回网络连接。

### 文件内容和浏览器显示的页面

HTML（HyperText Markup Language，超文本标记语言）是一组用尖括号标签标出标题、正文等结构的文字，浏览器读取后会把这些结构排成页面。固定版本把 `plain.html` 放在仓库相对路径 `web-server/code/03-handlers/plain.html`。文件的九行完整内容如下；这不是浏览器截图，而是服务器将读取的原始文件，来源定位为 [原行 1–9](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/plain.html#L1-L9)：

```html
<html>
<head>
<title>Plain Page</title>
</head>
<body>
<h1>Plain Page</h1>
<p>Nothin' but HTML.</p>
</body>
</html>
```

`html` 根元素包住整个 HTML 文档；`head` 放文档信息，`title` 给文档一个标题；`body` 包住页面主体。主体里，`h1` 表示最高层级标题，`p` 表示一段正文。于是这九行给浏览器的可见结果是标题 `Plain Page` 和正文 `Nothin' but HTML.`；`title` 则用作文档标题。服务器不把这些标签画出来，而是按字节传回；响应头中的 `Content-Type: text/html` 告诉浏览器把正文作为 HTML 解析。可对照 [MDN 的标题元素说明](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/heading_elements)、[`p` 段落元素](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/p) 和 [`title` 文档标题元素](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/title)。

### 浏览器发送请求，服务器返回响应

一次典型请求可以抽象成下面的起始行和头部。浏览器可能附带更多头部；这里只列出本课解释所需的部分：

```http
GET /plain.html HTTP/1.1
Host: 127.0.0.1:8080

```

`GET` 是读取资源的请求方法；`/plain.html` 是这次请求的目标；`HTTP/1.1` 是客户端声明的请求版本。`Host: 127.0.0.1:8080` 告诉服务器请求所指向的主机和端口；HTTP/1.1 请求通常包含这个头。起始行和头部以一个空行结束，之后才可能是请求正文；此处 GET 没有要发送的正文。服务器按项目规则尝试取文件，成功时给出 `200`（成功）响应；下面用占位正文表示状态行和头部：

```http
HTTP/1.0 200 OK
Content-type: text/html
Content-Length: <正文的字节数>

<html>...原文件正文...</html>
```

`HTTP/1.0 200 OK` 中 `200` 表示成功，`OK` 是对应短语；`Content-Type: text/html` 表示正文按 HTML 解释；`Content-Length` 说明正文有多少字节，尖括号只是占位符，实际代码会将 `len(content)` 转成十进制文字。固定原始文件为 116 字节，其中包括 9 个 LF 换行；若按这个版本原样以二进制读取并写出，长度值就是 `116`。这是静态字节计数，不是一次运行观察。标准库的 `send_response` 还会写 `Server` 与 `Date` 头。请求块和响应块中头部后面的空行标出头部结束；响应正文从其后开始。状态行使用 `HTTP/1.0`，即使浏览器请求行写 `HTTP/1.1`，因为 Python 2.7.18 的处理器默认 `protocol_version` 是 `HTTP/1.0`；请求版本与响应版本来自不同字段，不能假设相同。本课读完后，你应能沿这组具体值说明请求如何进入 `do_GET`、路径如何变成文件名、谁构造成功或失败响应，以及浏览器凭什么把返回字节当作 HTML；不会要求你安装或运行旧版 Python 才能阅读。

## 2. 系统位置与架构分工

图中的运行时对象与类关系分开画：浏览器在进程外；标准库服务器和项目处理器在同一个 Python 进程；文件系统通过操作系统 I/O 提供文件字节。TCP（Transmission Control Protocol，传输控制协议）让已连接的两端交换连续字节；本例的 HTTP 请求和响应都通过这条连接传送。实线是一次请求中的数据或调用，虚线是类继承关系；反向文件箭头表示读取结果返回给处理器。

```mermaid
flowchart LR
    B["浏览器与用户"]
    subgraph M["运行这份示例的一台计算机"]
        subgraph P["一个 Python 进程"]
            subgraph L["Python 2 标准库"]
                S["HTTPServer：监听并接受 TCP 连接"]
                H["BaseHTTPRequestHandler 基类代码：解析 HTTP 并分派方法"]
            end
            subgraph A["项目代码：server.py"]
                R["RequestHandler：项目请求处理器"]
                C["Cases：三种共享 case 对象"]
            end
        end
        F["操作系统文件系统：当前工作目录下的文件"]
    end
    B -->|"TCP 连接中的 HTTP 请求字节"| S
    S -->|"接受连接并构造处理器实例"| R
    R -.->|"静态类关系：继承并覆写"| H
    H -->|"同一实例上的解析与方法分派"| R
    R -->|"case.test(handler)，测试为 True 后调用 case.act(handler)"| C
    C -->|"act 内回调 handler.handle_file(full_path)"| R
    R -->|"open(full_path, rb)"| F
    F -->|"reader.read() 返回文件字节"| R
    R -->|"wfile 将状态行、头部和正文写入已接受连接"| B
```

`HTTPServer` 的项目创建点在 [`server.py` 原行 105–108](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L105-L108)；它继承的标准库 `HTTPServer` 再继承同步 `TCPServer`，其 socket 建立、绑定与监听见 [CPython 2.7.18 `BaseHTTPServer.py` 原行 102–111](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L102-L111)、[`SocketServer.py` 原行 413–443](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L413-L443)。

项目处理器的定义与规则表在 [`server.py` 原行 44–52](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L44-L52)；它继承的基类是 [CPython 2.7.18 `BaseHTTPServer.py` 原行 114](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L114)，该基类再通过 [SocketServer 的流连接处理器与 `rfile`/`wfile` 设置](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L677-L706)接入 socket。基类代码从连接读请求行、头部，并将请求字段派发给覆写方法；项目的 `RequestHandler` 提供 `do_GET`、文件读取、错误页和正文写出，不自行监听 TCP 端口或解析请求行。

实际数据链从 [`do_GET` 构造 `full_path` 与遍历规则](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L65-L79)开始，经 [`handle_file` 读取字节](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L81-L88)，再到 [`send_content` 输出](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L95-L101)。`open(...)` 请求操作系统文件读取能力，读出的字节回到 Python 处理器；响应经标准库提供的写流返回到同一已接受连接。图里的“文件系统”不是 Python 项目内部的另一个控制器。

### 模块、进程和继承关系

模块是保存类和函数定义的源文件单位；进程是操作系统启动后执行这些定义、创建服务器对象的运行单位。本例的 `server.py` 模块和导入的标准库模块都在同一个 Python 进程里，不代表它们分别运行成服务器进程。`RequestHandler` 是类；标准库接收连接后才调用这个类构造一个处理器实例。图中虚线表示类继承关系，实线表示运行时调用或字节流动，因此“基类代码调用覆写方法”仍是在同一个实例上发生，不是两个 handler 互相转发。

### 类属性和每连接的实例状态
模块执行到 `class RequestHandler` 时会执行类体，并建立 `Cases` 列表和三个 case 实例；此时还没有客户端连接。之后主入口创建 `HTTPServer`，服务器对象持有监听 socket 与 `RequestHandler` 类。一个客户端 TCP 连接被接受后，标准库才创建该连接的 handler 实例；默认 HTTP/1.0 响应设置使它通常只处理这个连接上的一个请求。`self.path`、`self.command`、`self.full_path`、`rfile`、`wfile` 属于这次连接的 handler 实例；文件内容则是 `handle_file` 中局部变量 `content` 的值。`RequestHandler.Cases` 是类属性，多个 handler 实例访问同一列表；列表里的 case 对象不保存某个用户的路径，而是调用时接收当前 handler。

### 规则对象怎样回调当前处理器
图中的箭头按调用方向读。`do_GET` 循环拿到一个 case 后执行 `case.test(handler)`；在 `test` 方法里，点号左边的 case 绑定为该方法的 `self`，括号中的 handler 是显式参数 `handler`。结果为真时，处理器再调用 `case.act(handler)`；`act` 中 `self` 仍是 case，参数仍是当前 handler。接着 case 执行 `handler.handle_file(full_path)`，所以图上有一条从 case 回到 handler 的回调箭头。它表示真实方法调用，不表示 case 继承自 handler，也不表示项目代码和标准库各有一个独立处理器。

这条边界适合展示本课的实际责任：通用网络协议由标准库处理，项目代码只回答“这个请求路径对应什么文件、怎样读、怎样把成功或失败写回去”。若把请求行解析也塞进 `RequestHandler`，项目就需要重新处理协议细节；若把文件选择交给标准库，这份代码中的 `Cases` 和文件映射规则又失去作用。当前 `HTTPServer` 是同步的 `TCPServer` 子类，没有混入线程服务器；一个请求处理期间，主服务循环不会并行处理另一个连接。慢文件读取或慢客户端因此可能拖住后续请求，这一点来自实际运行类，不是图中额外虚构出的工作队列。

## 3. 读懂本课所需的概念

### HTTP 消息怎样把请求和正文分开

浏览器是客户端：它提出取回页面的请求；服务器是接收请求并回送答复的程序。HTTP（Hypertext Transfer Protocol，超文本传输协议）约定请求和响应的消息结构。HTTP/1.1 消息由起始行、头部行、一个空行和可选正文组成；起始行和每个头部行以 `CRLF` 结束，CRLF 是 Carriage Return Line Feed（回车换行，即 `\r\n`）。请求起始行依次给出方法、请求目标和版本，例如 `GET /plain.html HTTP/1.1`；响应起始行给出服务器使用的版本、状态码和说明文字。空行结束头部，后面的字节才属于正文。可对照 [RFC 9112 的消息格式](https://www.rfc-editor.org/rfc/rfc9112.html#section-2.1) 与 [`Content-Length` 定义](https://www.rfc-editor.org/rfc/rfc9112.html#section-6.2)。本项目是 Python 2 时代的 HTTP/1.0 默认响应示例；RFC 9112 在此只帮助理解消息边界，不证明项目完整支持 HTTP/1.1。

TCP（Transmission Control Protocol，传输控制协议）把已连接的两端表现为连续字节流；它不替应用程序标出 HTTP 头部在哪里结束。标准库读请求行、各头部行和空行，才得到 HTTP 字段边界。`wfile.write(...)` 把响应字节交给这个 TCP 连接的输出流；调用返回不表示浏览器已收到全部字节。

把两层放回这一次请求里：浏览器先把 `GET /plain.html HTTP/1.1` 编成字节交给 TCP；TCP 尽力按顺序把字节送到连接另一端，却不认识 `GET`、头部或 HTML。HTTP 才规定接收端如何把这些字节读成请求行、头部和正文。反方向也一样：TCP 不会替项目挑 `200`，是项目/标准库按 HTTP 规则写出状态行与头部，再把它们连同正文交给 TCP。

头部结束空行的意义是让解析器知道从哪里开始才是正文；`Content-Length` 则在正文长度需要明确时说明后续有多少个八位字节。它写的是字节数，不是字符数。请求和响应的换行符是协议边界的一部分，不能把看起来空白的那一行删掉后还声称消息结构相同。RFC 9112 解释的是通用 HTTP/1.1 消息格式；本课项目按 Python 2.7.18 默认发送 HTTP/1.0 响应，不因此获得完整 HTTP/1.1 能力。

#### 同一请求在传输层、HTTP层和socket对象上的不同读法

用本课输入做一张消息边界图。它是教学示意，不是程序抓包记录：

```text
浏览器交给 TCP 连接的有序字节：
GET /plain.html HTTP/1.1\r\n
Host: 127.0.0.1:8080\r\n
\r\n
[可选的请求正文字节]

HTTP 解析器据此识别：
起始行 = 方法 GET | 目标 /plain.html | 版本 HTTP/1.1
头部行 = Host: 127.0.0.1:8080
空行 = 头部结束；其后的字节才属于正文

当前连接的 socket/rfile = 程序从这条已接通通道读取上述字节的接口
```

第一部分是 TCP 能看到的顺序字节；它不理解 `GET` 或 `Host` 的含义，也不知道头部在哪结束。HTTP 解析器按 `CRLF` 读起始行和头部，并把空行作为边界；若请求正文存在，才从空行后读取正文。`socket` 是程序手上的连接对象，`rfile` 是标准库用该连接包装出的读取接口，它们都不替代 HTTP 规则。项目拿到解析后的 `self.path`，是在这几步之后；它再把目标文字交给文件路径拼接逻辑。

### URL 目标、网络地址和文件路径分别是谁

URL（Uniform Resource Locator，统一资源定位符）把访问方案、主机、端口和目标写在一起；它不是磁盘路径。这里 `http` 是 URL 的 scheme（访问方式前缀），选择 HTTP 访问；`127.0.0.1` 是 IPv4（Internet Protocol version 4，互联网协议第 4 版）地址，`8080` 是服务器监听端口，`/plain.html` 是请求目标。IP（Internet Protocol，互联网协议）是网络寻址协议；IPv4 是地址格式之一。本例的 `127.0.0.1` 是回环地址，表示连接回到发起它的本机，不代表所有服务器地址。

端口让操作系统把到达某个监听端口的连接交给相应 socket。socket（套接字）是程序操作网络连接一端的对象；它不是磁盘文件。URL 中的 `/plain.html` 只是发来的目标文字，不会自动成为服务器上的 `/plain.html` 文件。标准库把目标存到 `self.path`；项目随后才用 `os.getcwd() + self.path` 构造文件路径。因此当前工作目录、请求目标和最终磁盘路径是三个不同值；查询文字也仍包含在本例的 `self.path` 中。Python 的 tuple（元组）按顺序保存多个值；入口中的 `('', 8080)` 是一个二元组，第一项为空主机文字，第二项是端口整数 `8080`。

沿着值走一遍就能分清这些名字：浏览器地址 `http://127.0.0.1:8080/plain.html` 中，`127.0.0.1` 是本机回环地址，`8080` 是连接目标端口，`/plain.html` 是随 HTTP 请求发送的目标文字。入口另有绑定值 `('', 8080)`；空主机表示在本机 IPv4 接口上监听，不是请求中的 `127.0.0.1`。监听 socket 等连接；TCP `accept()` 之后得到的已连接 socket 才承载某个客户端的字节流。标准库把这条连接交给新 handler，HTTP 解析后 `self.path` 仍是 `/plain.html`。最后项目用进程当前工作目录拼出 `/work/500lines/web-server/code/03-handlers/plain.html`，这个字符串才交给文件系统打开。

所以至少有四种不能互换的东西：监听地址决定程序在哪里等连接；已连接 socket 对应一条已经接通的网络通道；URL/请求目标告诉服务器客户端要什么；磁盘路径告诉操作系统程序要读哪个本地文件。改请求目标不等于改服务器监听地址，改 URL 中的端口也不等于改源码里的文件目录。本项目把 `?rev=2` 也留在 `self.path` 并直接拼进路径，说明它没有单独解析查询参数。

### 类、实例、方法参数怎样组成这条调用

类是一种对象定义，实例是按类创建的具体对象。Python 2 的内置基类 `object` 出现在 `class case_no_file(object)` 中；`case_no_file()` 的括号会创建实例。`class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler)` 则表示项目处理器继承标准库处理器，保留基类的连接读取和请求分派，再覆写同名 `do_GET` 方法加入文件服务行为。

Python 源文件也可以作为模块被其他代码导入；`import os` 让当前模块能用名字 `os` 访问它。解释器给模块提供 `__name__`：直接运行文件时它是 `'__main__'`，被导入时通常是模块名。`==` 比较两边的值是否相等，结果是布尔值；因此 `if __name__ == '__main__':` 只在直接运行时进入缩进的入口代码。`sys.argv` 是包含脚本名和命令行参数的列表；源码虽然导入 `sys`，但没有读取它，所以不能从文件名或 README 推断它会处理目录参数。

`def method(self, handler):` 定义方法及它接收的参数；冒号后的缩进语句属于方法体。参数是函数声明中接收值的名字，调用时传入的值是实参。对象方法调用 `case.test(current_handler)` 会把 `case` 自动绑定为方法里的 `self`，而显式传入的 `current_handler` 才绑定到 `handler`。所以源码里 `case.test(self)` 这一行有**两个不同的 `self`**：外层 `self` 是当前 `RequestHandler` 实例；进入 `test` 后，方法里的 `self` 则是 case 实例，`handler` 才是刚才的处理器。相同名字不会让它们变成同一个对象。

点号 `.` 用来从对象或模块取属性：`os.getcwd` 是从 `os` 模块取函数，`handler.full_path` 是从当前处理器实例取路径状态，`self.Cases` 则会沿类查找到共享列表。普通 `do_GET(self)` 由标准库以绑定方法形式调用，所以当前处理器会自动成为 `self`；项目不再显式传一次自身。类或方法体第一条三引号字符串可以是 docstring（文档字符串）；多行三引号也可保存模板文字，原模板开头的反斜线会去掉开头换行。`pass` 是语法占位语句，执行时不增加动作。

把这些对象分开看：`.py` 文件作为模块在一个 Python 进程里执行；模块不是新进程。直接运行时 `__name__` 是 `'__main__'`，入口创建一份服务器实例。`RequestHandler` 是类，也就是一份对象定义；服务器收到连接后才按这个类创建处理器实例。`case_no_file` 同样是类，`case_no_file()` 才创建一个规则对象。`Cases` 在处理器类体执行时建立，三个规则实例随后跨连接共享；本请求的 `full_path` 则属于具体 handler。把请求路径放进 `Cases` 会让共享对象持有易变的连接数据，下一条请求可能覆盖上一条请求的值。

`class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler)` 表达继承：项目类得到标准库处理器的连接字段、读请求和分派能力。项目又定义同名 `do_GET`，这叫覆写；标准库仍做通用 HTTP 工作，到 GET 分派点时执行项目版本。这里 library 和 project 不是两个 handler：运行时是一个 `RequestHandler` 实例，基类代码和项目覆写方法都在同一个实例上工作。派生类沿用通用步骤，只替换当前项目要定制的那个方法。

Python 方法的第一个参数名 `self` 是约定，不是关键字；点号调用时，点号左边的对象会绑定给这个参数。比如 `case.test(self)` 中，外层 `self` 是 handler，点号左边的 `case` 进入 `test` 内部成为它自己的 `self`，括号中的 handler 则成为 `handler`。因此 `handler.full_path` 读请求路径，`self` 指规则实例。名称相同不等于对象相同。标准库调用绑定的 `do_GET()` 时不显式传参数，当前 handler 自动绑定为该方法的 `self`。

### 条件、循环和返回值怎样选择一个 case

`Cases` 列表按顺序装三个 case 实例。`for case in self.Cases` 逐个取出它们；`if case.test(self)` 先调用规则的 `test`。`True` 和 `False` 是布尔值：`case_no_file.test` 在 `exists` 为假时用 `not` 取反并返回真，文件规则再用 `isfile` 判断是不是普通文件。`return expression` 结束这次方法调用并把表达式结果交给调用者，因此 `test` 返回的布尔值决定 `if` 的分支。

匹配后，`case.act(self)` 执行实际动作。`None` 是 Python 表示“没有交回具体结果”的特殊对象；这些方法没有显式 `return`，正常结束时仍会把 `None` 交给调用者。`do_GET` 不使用这个返回值，因为动作已经由 `handle_file` 写响应或由 `raise` 抛出错误完成。`break` 只在动作正常返回后执行，离开最近的 `for` 循环。兜底 case 的 `test` 永远返回 `True`，所以它必须在列表末尾，否则前面的请求会被它抢先截住。

用 `/plain.html` 的值逐步读条件：`for` 先令局部变量 `case` 指向 `Cases` 的第一个对象；`case.test(self)` 调用它的判断方法；`return not os.path.exists(...)` 交回布尔值，`if` 只在值为真时进入缩进的动作。第一条返回假，循环继续；第二条 `isfile(...)` 返回真，才调用 `act`。匹配表示选择动作，不表示自动离开循环；只有 `act` 正常返回，下一句 `break` 才执行。若 `act` 抛异常，控制直接跳到最近匹配的 `except`，`break` 不会执行。这个顺序也是为什么恒真兜底规则必须最后放。

把实际循环代码与对象绑定放在一起看。源码位置：`server.py` 原行 72–75，`RequestHandler.do_GET`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L72-L75)。代码末尾的中文行尾内容是明确标出的教学注释。

```python
            for case in self.Cases:
                if case.test(self):  # 教学注释：把当前 handler 显式传给 case 的判断方法。
                    case.act(self)  # 教学注释：执行首个匹配规则的动作。
                    break  # 教学注释：动作正常返回后不再检查后续规则。
```

代入具体对象：当前处理器记作 `H`，`H.full_path` 是 `/work/500lines/web-server/code/03-handlers/plain.html`；共享列表前两个对象分别记作 `N=case_no_file()`、`E=case_existing_file()`。教学示意中的每一步是：

```text
第一次循环：case = N
case.test(H) 绑定为 N.test(self=N, handler=H)
exists(H.full_path) = True，所以 N.test 返回 not True = False
if False：不调用 N.act；for 取下一个对象

第二次循环：case = E
case.test(H) 绑定为 E.test(self=E, handler=H)
isfile(H.full_path) = True，所以 E.test 返回 True
进入 if：E.act(H) 调用 H.handle_file(H.full_path)
```

外层 `do_GET` 的 `self` 是 `H`；表达式 `case.test(self)` 中点号左边 `case` 自动绑定为 `test` 里的 `self`，括号中的 `H` 才绑定到显式参数 `handler`。第一行 `for` 不新建 case，它只是让局部变量 `case` 依次指向列表中已有的对象。`return` 把测试结果交给 `if`；`if` 消费这个布尔值；动作调用的 `None` 返回值不会被保存。文件动作正常返回后，下一行 `break` 结束扫描；这条调用说明了为什么方法签名里有两个不同角色，即使变量名 `self` 重复。

方法可能用两种方式改变程序：`return` 把值交给调用者，写字段/写网络等动作则在对象或外部系统留下副作用。`test` 返回真假；`act` 不显式返回值，成功时返回 `None`，但 `handle_file` 已经尝试写响应。HTTP 的状态码仍不是 Python 返回值：异常先在 Python 内传播，只有错误处理代码调用 `send_content(..., 404)` 后，404 才成为要写入的 HTTP 状态。宽泛的 `except Exception` 会把很多普通程序错误也转成项目错误页，这属于当前代码的实际取舍。

### Python 异常和 HTTP 状态不是同一种结果

`raise ServerException(...)` 抛出 Python 异常，会中断当前正常语句并沿调用链寻找匹配的 `except`。`try` 标出可能失败的语句范围；`IOError` 是 Python 输入/输出操作的异常，`except IOError as msg` 接住它并把异常对象绑定到 `msg`。`except Exception as msg` 也能接住它以及其他普通异常。本例 `do_GET` 的 `except Exception as msg` 把缺失路径异常交给 `handle_error`；它也会接住其他普通程序错误，所以项目内部错误可能被误显示成文件访问错误。

`404` 则是 HTTP 响应中的状态码，表示当前目标未找到。异常不会自动写状态行或 HTML 页面；只有 `send_content(content, 404)` 才把状态码写入响应。成功调用 `send_content(content)` 省略状态参数，Python 使用签名中的默认值 `status=200`。相同的发送方法因此由调用点选择成功还是失败的语义。

字符串的 `.format(...)` 会把花括号占位符替换成调用者给的值。`"'{0}' not found".format('/missing.html')` 用第一个位置实参替换 `{0}`，得到 `"'/missing.html' not found"`；`"{path}: {msg}".format(path=self.path, msg=error)` 则按名字填两个占位符。`path=...` 和 `msg=...` 是传给格式化方法的关键字实参，不会给 `self` 的字段赋值；这也是错误页模板把请求路径和异常说明组合成正文的方式。

### 文件字节怎样成为浏览器能解释的 HTML

Python 2 的普通 `str` 是字节串；`unicode` 是保存已解码文字字符的文本类型，可以先把它理解成字符层面的内容。`open(full_path, 'rb')` 中 `r` 表示读取，`b` 表示不解码、保留字节；`.read()` 在本例得到 `plain.html` 的字节串。`with open(...) as reader` 把文件对象暂时绑定给 `reader`，离开缩进块时关闭它，即使读取抛出异常也会执行清理。这里一次读完整份小文件，因此内容会暂存在内存。

`Content-Type: text/html` 告诉浏览器正文应按 HTML 解释，不会转换文件内容。ASCII（American Standard Code for Information Interchange，美国信息交换标准代码）是常见英文字母、数字和标点的基本编码；这份 `plain.html` 只含 ASCII 字符，所以对它来说**字符数和字节数恰好相等**。`len(content)` 实际数的是读入的字节；HTTP 的 `Content-Length` 也声明正文的八位字节数量。Unicode 是不同文字字符的统一表示；Python 2 的 `unicode` 类型表达这种已解码文字，而不是原始文件字节。若文件中有 UTF-8 编码的 `中`，它是一个 Unicode 字符、在读入的 UTF-8 字节串中占三个字节，因此**字节数不是字符数**，用字符数代替编码后字节数会算错长度。`str(len(content))` 把字节整数转成头部所需的十进制文字；`wfile` 是标准库围绕已接受 socket 建立的输出文件接口。

这两种类型回答不同问题：Unicode 文本表示“是什么文字”，编码后的 `str` 表示“线上实际是哪几个字节”。UTF-8（8-bit Unicode Transformation Format，8 位 Unicode 转换格式）把 Unicode 字符编码成一串字节；常见 ASCII 字符在 UTF-8 中仍各占一个字节，而 `中` 的 UTF-8 序列是三个字节。若发送文本，正确顺序是先选编码得到最终字节，再对这些字节计算 `Content-Length`。本例用 `'rb'` 直接读取仓库文件，得到的已经是待发送字节，所以 `len(content)` 不需要把字符再编码一次。

下面是 Python 2 的教学示意，不是项目源码；`u` 前缀让字面量成为 `unicode` 文本。文件顶部的编码声明让 Python 2 能读入源码里的中文字符。

```python
# -*- coding: utf-8 -*-  # 教学示意：声明此示意文件的源文字编码。
text = u'中'  # 教学示意：一个 Unicode 字符。
encoded = text.encode('utf-8')  # 教学示意：把该字符转换成 Python 2 字节串。
len(text)  # 教学示意：结果为 1 个字符。
len(encoded)  # 教学示意：结果为 3 个字节。
encoded  # 教学示意：Python 2 的 repr 显示为 '\xe4\xb8\xad'。
```

`text` 保存一个字符；`U+4E2D` 是 Unicode 码点记号，也就是该字符在 Unicode 编号表中的编号。`encode('utf-8')` 把它变成三个字节，十六进制值依次为 `E4 B8 AD`：十六进制是以 16 为基数的写法，每两个数字表示一个字节，所以这里有三个字节。Python 2 中 `len(text) == 1`，而 `len(encoded) == 3`。最后一行显示的是三个字节的转义记法，不是字符数量；反斜线转义是 Python 用来显示字节值的记法。实际项目的 `content` 来自 `open(..., 'rb').read()`，已经是文件字节；`send_content` 原行 99 用 `str(len(content))` 把这些字节数写入 `Content-Length`。若把 Unicode 文本直接发送，先编码再计数才会得到与正文吻合的长度。

文件换行也计入总字节数。固定提交里的 `plain.html` 共 116 字节，其中有 9 个 LF 换行；若只把这 9 个 LF 各换成 CRLF，每处多一个字节，长度静态计算为 125。这里没有执行服务器，只是在源文件字节上计数。长度头若按字符数或另一份换行格式计算，浏览器看到的边界就可能与实际发送正文不一致。

`with open(..., 'rb') as reader` 同时表达资源的临时所有权：进入 `with` 取得文件对象，缩进块里的 `reader.read()` 读取字节，离开块时文件自动关闭。`read()` 若抛 `IOError`，清理仍先发生，再由外层 `except IOError` 接手；正常读取时也是先关文件再写网络响应。若不使用 `with`，每个退出分支都要正确关闭文件，任何漏掉的异常分支都会留下未关闭资源。注意 `try` 还包住随后的 `send_content`，所以同一段 `except IOError` 也会接住网络写错误。

最后看有序规则表为什么能工作：它把每条规则拆成 `test` 判断和 `act` 动作，处理器按列表从上到下只执行第一个匹配动作。对于普通文件，先排除缺失，再识别文件，最后才让恒真兜底接住剩余目标。把兜底提前会让后续规则永远到不了；把规则写成一长串 `if/elif` 也能完成当前两种判断，但新增目录首页规则时会把判断和发送动作混在一个方法里。当前列表让新 case 可插在文件规则和兜底之间，代价是读者必须理解顺序依赖；这只是这份程序的有序规则设计，不表示它有插件扫描或动态注册系统。


## 4. 端到端流程与本课边界

### 启动阶段：先建规则表，再开始监听

为让路径值可以复算，以下静态示例假设仓库检出在 `/work/500lines`，启动进程时的当前工作目录为 `/work/500lines/web-server/code/03-handlers`。这是假设输入，不是本机运行记录。Python 按文件顺序先执行导入和类定义；执行 `class RequestHandler` 的类体时，原行 50–52 的三个 `case_*()` 调用立即创建三个共享对象。它发生在文件末尾主程序创建服务器之前，所以启动时已有规则列表，但还没有任何连接处理器。

文件定义全部完成后，`if __name__ == '__main__'` 才进入入口。`serverAddress = ('', 8080)` 把 IPv4 主机值与端口组成二元组。该版 socket 文档说明 IPv4 的空主机字符串代表 `INADDR_ANY`，即“任意本地 IPv4 接口”的地址常量，因此服务器绑定本机所有可用 IPv4 接口，而非只绑 `127.0.0.1`。`BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)` 把监听地址和处理器类交给标准库；服务器构造 socket、绑定并监听，随后 `serve_forever()` 等待连接；构造与 `listen()` 的位置见 [CPython 2.7.18 `SocketServer.py` 原行 413–443](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L413-L443)。入口和监听配置位于 [项目 `server.py` 原行 105–108](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L105-L108)，空主机的语义见 [CPython 2.7.18 socket 文档原行 54–58](https://github.com/python/cpython/blob/v2.7.18/Doc/library/socket.rst#L54-L58)。源码不读取命令行参数；启动目录取自进程当前工作目录，端口直接写在 tuple 中。

### 一次请求：连接被接受后才产生处理器实例

用户输入 `http://127.0.0.1:8080/plain.html` 后，浏览器对本机 8080 端口建立 TCP 连接，并在连接中写入请求。`serve_forever()` 轮询监听 socket；连接就绪时，标准库取出已接受 socket 和客户端地址，再沿同步默认路径创建处理器。`HTTPServer` 持有 `RequestHandler` 类；它不预先创建实例。每个被接受的连接才构造一个 `RequestHandler` 实例，实例绑定该连接的 `request`、客户端地址和服务器对象。

```mermaid
sequenceDiagram
    participant B as 浏览器
    participant S as HTTPServer 监听实例
    participant H as 当前 RequestHandler 实例（同一实例执行基类代码）
    participant C as Cases 中的 case 对象
    participant F as 操作系统文件系统
    B->>S: 建立到监听端口的 TCP 连接
    S->>H: accept 后以已连接 socket、地址和服务器对象构造实例
    H->>H: setup 建立 rfile/wfile，handle 开始解析
    B->>H: 在已连接 socket 上发送 GET /plain.html HTTP/1.1
    H->>H: parse_request 设置 command、path、request_version
    H->>H: handle_one_request 查找并调用绑定的 do_GET
    H->>H: full_path = 当前工作目录 + self.path
    H->>C: 依次调用 test(handler)，找到文件 case
    C-->>H: case_existing_file.test 返回 True
    H->>C: 调用 case_existing_file.act(handler)
    C->>H: 调用 handle_file(full_path)
    H->>F: open(full_path, rb)，read 全部文件字节
    F-->>H: 返回 plain.html 字节
    H-->>B: 在同一连接写出状态、头部和正文
    B-->>B: 解析 text/html 正文，显示标题和段落
```

标准库 `BaseRequestHandler` 构造函数先存放 socket、客户端地址和服务器对象，再调用 `setup()`、`handle()`，最后清理；流处理器的 `setup()` 给同一连接建立 `rfile` 和 `wfile`。因此图中 `H` 是一个 handler 实例，基类方法和覆写方法都在它身上运行。服务器只接受连接并创建 handler；真正读请求行、识别 `GET` 并调用项目 `do_GET` 的是这个实例内部的 HTTP 基类分派代码，不是 `HTTPServer` 直接调用项目方法。[生命周期的原文位置](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L649-L717)。

处理器构造发生在同步调用栈里：`BaseRequestHandler.__init__` 先存下三个字段，再 `setup()`；接着调用 `handle()`，并由 `finally` 执行 `finish()`。所以正常读完或处理过程中抛异常，handler 的收尾都会尝试刷新、关闭 `wfile` 和关闭 `rfile`。若 `handle()` 抛出的异常没有被项目接住，它会返回到服务器的 `process_request` 路径，由 `_handle_request_noblock` 调用服务器错误钩子并关闭已接受 socket；项目自己接住的 `ServerException` 则按第5章路径转成 404，不会走到这条未处理异常分支。`setup()` 本身位于 `try` 外，若资源建立阶段抛错，`finish()` 不会由这段 `finally` 执行。方法顺序和异常边界见 [CPython 2.7.18 `BaseRequestHandler.__init__`](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L649-L657) 与 [`BaseHTTPRequestHandler.handle`](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L336-L343)。

### 从请求行到文件路径：每次值变化由谁负责

对图中请求行 `GET /plain.html HTTP/1.1`，基类解析后把 `self.command` 设为 `'GET'`，把 `self.path` 设为 `'/plain.html'`，把 `self.request_version` 设为 `'HTTP/1.1'`。接着基类按 `do_` 加方法名的规则，在同一个实例上找到 `do_GET` 并调用。项目路径赋值所在位置是 [`server.py` 原行 64–79](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L64-L79)；基类解析与方法查找分别见 [`BaseHTTPServer.py` 原行 232–299](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L232-L299) 和 [原行 301–343](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L301-L343)。

本次静态值中，`os.getcwd()` 是 `/work/500lines/web-server/code/03-handlers`，`self.path` 是 `/plain.html`，所以 `self.full_path` 变成 `/work/500lines/web-server/code/03-handlers/plain.html`。这是项目的字符串拼接结果，不是标准库将 URL 自动转换成文件路径。随后循环先问缺失规则：`exists(full_path)` 为真，取反后该 case 返回 `False`；再问普通文件规则：`isfile(full_path)` 为真，选中它并调用 `act`。只有 `act` 正常返回后，`do_GET` 才执行 `break` 停止继续检查；`case_always_fail` 只有前两条都没处理时才轮到。

### 从选中的 case 到响应正文：文件字节由调用方消费

文件 case 把同一个 `full_path` 交给当前处理器的 `handle_file`。本例 `open(full_path, 'rb')` 返回二进制 reader，`read()` 读出 `plain.html` 九行字节；退出 `with` 块后文件关闭。成功路径随后调用 `send_content(content)`，没有传第二个参数，因此使用默认 `status=200`。这两个调用依次发生在 [`case_existing_file.act` 原行 22–29](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L22-L29)、[`handle_file` 原行 81–88](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L81-L88) 和 [`send_content` 原行 95–101](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L95-L101)。

`send_content` 先调用标准库 `send_response(200)`，再写项目选择的 `Content-type: text/html` 与按字节计算的 `Content-Length`，用空行结束头部，最后把正文交给 `wfile`。Python 2.7.18 的默认 `protocol_version` 使状态行是 `HTTP/1.0 200 OK`，即使输入请求写 `HTTP/1.1`。浏览器读取到完整响应后，按 `text/html` 解析原来的标签，页面主体显示 `Plain Page` 与 `Nothin' but HTML.`；`title` 是文档标题。`wfile.write` 调用只表明程序尝试向连接写字节，并不证明网络完整送达或浏览器成功绘制，本课没有实际观察这一步。

本课的链路范围是这一个 `GET /plain.html` 成功路径、缺失/非文件路径错误，以及它们依赖的标准库连接建立与分派。启动装配和每个请求的生命周期已分别追踪；浏览器缓存、CSS、JavaScript、域名解析与 TLS 不参与这份示例的文件读取链，因此不在本课展开。


## 5. 真实源码逐段逐行精读

本章按理解依赖排列：先看规则和处理器怎样定义，再看各方法，最后回到启动入口。这个排列不是运行时调用顺序；实际启动及一次请求的次序见第四章。每块均取自固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2` 的 [项目原文件 `web-server/code/03-handlers/server.py`](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L1-L108)，原文件 108 行、LF 换行。下面的代码块保留原语句、原注释和代码单元内部空白；若为帮助初读者在源码行旁增加行尾中文内容，会明确标成“教学注释”，不把它算作固定提交的原文。为便于阅读，独立职责块之间略去原文件的空白分隔行和 `#-----` 注释线。

### 5.1 先准备路径工具和一个可传递的项目异常

#### 为什么先看这段定义

当前请求可能命中“找不到文件”或“路径不是普通文件”。这两种情况都要从规则对象退回到处理器的统一错误出口。先看它依赖的模块和项目异常定义，来源是原行 1–7：

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `ServerException` 与模块导入；原行 1–7；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L1-L7)。

#### 完整原文

```python
import sys, os, BaseHTTPServer

#-------------------------------------------------------------------------------

class ServerException(Exception):
    '''For internal error reporting.'''
    pass
```

#### 原行 1–7：名字从哪里来，异常又往哪里去

原行 1 一次导入三个模块名：后文用 `os.getcwd`、`os.path.exists` 和 `os.path.isfile`；`BaseHTTPServer` 提供历史版 HTTP 处理器；`sys` 虽然导入了，但这份文件没有使用它，也没有因此读取命令行参数。原行 3 的横线只是源文件分隔注释。

原行 5 定义 `ServerException`，括号里的 `Exception` 是 Python 内置异常基类；继承它使项目能像其他异常一样抛出和捕获这个类型。原行 6 的三引号字符串是类的文档字符串，说明它用于内部错误报告。原行 7 的 `pass` 表示类暂时没有再添加字段或方法；之后规则仍可构造并 `raise ServerException(...)`，让调用栈跳回 `do_GET` 的 `except`。

这里并没有在定义类时产生一次 HTTP 错误。执行 `raise ServerException(...)` 才创建并抛出异常对象；规则动作里抛出的对象沿调用栈向外走，直到 `do_GET` 的 `except Exception as msg` 接住它，再传给 `handle_error`。异常只是 Python 内部的控制流和说明文字，不自带 404；HTTP 状态要等 `send_content(content, 404)` 才写入。

项目自定义异常的好处是可以用一个名字表示“规则判定的项目级失败”，而不把它与 `IOError` 混为一谈。实际处理器仍然捕获所有 `Exception`，所以这条区别没有转化成不同状态码；若项目要区分路径失败、权限失败和程序缺陷，下一步应缩窄捕获范围并分别处理，而不是指望异常类名自动选择响应。

### 5.2 缺失规则先判断路径是否存在

#### 实际问题、调用位置与输入准备

处理器已经为本次请求保存 `handler.full_path`。当它指向不存在的文件或目录时，第一条规则要返回真并中断正常分支；规则对象本身不写网络响应。以下为原行 11–18：

`do_GET` 在原行 72–74 按表调用 `case.test(self)`，只有测试返回真才调用同一个对象的 `case.act(self)`。本次演算使用工作目录 `/work/500lines/web-server/code/03-handlers` 和请求目标 `/missing.html`，所以 handler 带入规则的 `full_path` 是 `/work/500lines/web-server/code/03-handlers/missing.html`。`test` 应只回答路径是否存在；错误正文和网络响应由动作之后的处理器出口完成。

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `case_no_file.test`、`case_no_file.act`；原行 11–18；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L11-L18)。

#### 完整原文

```python
class case_no_file(object):
    '''File or directory does not exist.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)  # 教学注释：缺失路径时把规则判为匹配。

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))  # 教学注释：把用户看到的请求路径放进项目异常文字。
```

#### 原行 11–18：先返回判断，再抛出动作失败

原行 11 定义 `case_no_file` 类并继承内置 `object`；行 12 的 docstring 写明它代表文件或目录都不存在。每次请求复用的列表中会放此类的实例。

原行 14 的方法有两个参数：方法绑定时 `self` 自动是这个 case 对象，`handler` 则由调用点显式传入当前 `RequestHandler`。原行 15 读取该处理器的 `full_path`，`os.path.exists` 对文件或目录存在都返回真；`not` 将真假反转，因此缺失路径时 `return` 把 `True` 交给循环里的 `if`。这里返回的是**规则判断，不是 HTTP 响应**。

原行 17 定义对应动作。原行 18 用 `handler.path`（浏览器请求目标文字）替换格式串 `{0}`，形成例如 `'/missing.html' not found`，然后 `raise` 抛出自定义异常。`raise` 使本次 `act` 不会正常返回，调用处后面的 `break` 也不会执行；错误随后由处理器统一转换成响应。

把这两步按值连起来：文件系统对完整磁盘路径回答 `exists=False`；`not False` 得到 `True`；`if` 因而进入动作。`.format(handler.path)` 使用请求目标文字而不是绝对路径，异常内容成为 `'/missing.html' not found`。异常直接越过 `do_GET` 循环的剩余语句，最终由它的 `except` 调用错误页。若文件存在，测试返回假，动作根本不会运行，下一条规则继续检查。

#### 这一规则的设计结果与接入影响

把判断和动作分开，使同一条规则先给循环一个布尔值，选中后再抛出异常；若在 `test` 里直接写响应，循环就会把“判断一次”变成有副作用的操作，重复检查时更难推理。当前动作把缺失路径交给统一错误模板，因此新增规则时也要明确：它是返回 `False` 让后续规则尝试，还是返回 `True` 并以正常动作处理，还是像此处一样抛出项目异常。错误码由下游错误处理决定，不由这个 `test` 返回值决定。

### 5.3 存在且为普通文件时，把路径交给处理器读取

#### 实际问题、调用位置与输入准备

如果第一条规则判为假，第二条规则判断同一个路径是不是普通文件。匹配后，它必须调用能读取文件并发送结果的处理器方法；仅返回路径不会让浏览器收到正文。原行 22–29：

在 `/plain.html` 的成功路径中，传入 `handler.full_path` 的值是 `/work/500lines/web-server/code/03-handlers/plain.html`。第一条 `case_no_file.test` 得到假后，循环把同一个 handler 交给此处的 `test`。只有第二条返回真，`act` 才把该路径交给 handler 的 `handle_file`；下游负责打开文件和发送响应。

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `case_existing_file.test`、`case_existing_file.act`；原行 22–29；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L22-L29)。

#### 完整原文

```python
class case_existing_file(object):
    '''File exists.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)  # 教学注释：只在目标是普通文件时匹配。

    def act(self, handler):
        handler.handle_file(handler.full_path)  # 教学注释：把完整磁盘路径交给当前连接的处理器。
```

#### 原行 22–29：普通文件的判断和委托

原行 22–23 定义“文件存在”规则。原行 25 定义 `test` 方法，原行 26 才调用 `os.path.isfile`；它与上条的 `exists` 不同：目录虽然存在，但不会因此被当作普通文件。当前 `/plain.html` 映射到磁盘文件时它返回 `True`。

原行 28–29 的 `act` 接收同一个显式传入的 `handler`，从它取出 `full_path` 并调用 `handle_file`。该调用的返回值被规则忽略；实际结果依赖 `handle_file` 的写响应副作用。若文件在 `isfile` 检查之后消失，稍后的 `open` 仍可能失败，第5.7节会继续推演检查与打开之间的时序。

对成功输入，路径值在本规则里没有再次转换：`isfile(full_path)` 返回真，动作将同一字符串传给 `handle_file(full_path)`。`handle_file` 正常结束时隐式返回 `None`；`act` 也没有显式 `return`，因此 `do_GET` 不会拿到文件内容或响应对象。内容已经由 handler 的后续写操作送入连接，`break` 只负责停止规则扫描。

`isfile` 的回答只代表检查瞬间的文件系统状态，不会把文件锁住，也不保证下一步 `open` 一定成功。如果是目录，它返回假，循环继续到兜底规则；如果普通文件在两步间被删除，动作仍已选中，但打开会抛 `IOError`。扩展表时可复用此动作所接的 `handle_file`，前提是新规则传入的值确实是可打开的文件路径。

#### 代入运行：成功、读取失败和两个不同的返回路径

对 `/plain.html`，`handle_file` 读入字节，调用 `send_content(content)`；若写出正常，`send_content` 因没有显式 `return` 返回 `None`，`handle_file` 也到方法末尾隐式返回 `None`，`case_existing_file.act` 同样没有返回表达式，最终 `do_GET` 不接收这个值。执行顺序是 `handle_file → act → case.act(self) 返回 → break`；响应副作用已经发生，`None` 只表示没有另外交回内容值。

若 `open` 抛 `IOError`，文件对象尚未创建；若 `reader.read()` 抛 `IOError`，`with` 先关闭已打开的 reader，再进入 `handle_file` 内部 `except`。假设错误页写出正常，`handle_error` 和 `send_content` 正常结束并返回 `None`；`handle_file` 的 except 走到末尾也正常返回 `None`，因此 `act` 返回到 `do_GET`，`break` 仍会执行。与之相反，缺失 case 的 `act` 抛 `ServerException`，它没有在 action 内部捕获；所以它不返回给循环，`break` 被跳过，外层 `do_GET` 的 except 接手。这是“异常控制流”和“正常返回 None”两种不同路径。

#### 设计与接入：为什么测试普通文件要用 `isfile`

假设请求 `/subdir` 指向现存目录：`os.path.exists(full_path)` 会给真，但 `os.path.isfile(full_path)` 给假。规则要识别可由 `open(..., 'rb')` 读取为普通文件的目标，因此使用 `isfile`；若把它误改为 `exists`，目录会匹配文件 case，动作就尝试把目录交给 `handle_file`，在拒绝按普通文件打开目录的系统上会走 `IOError` 错误页，而不是目录首页。目录是否应提供 `index.html` 是另一个明确规则，见第八章变体。新增文件规则时要接在缺失规则后、恒真规则前，并继续传入 handler 的 `full_path`，否则已有消费者收到的值类型会改变。

### 5.4 兜底规则让未识别路径有明确出口

#### 实际问题、调用位置与输入准备

存在的目录会使 `exists` 为真、`isfile` 为假；它不会匹配前两条规则。第三条规则接住这种情况，也接住其他未匹配目标。它必须排在列表末尾。原行 33–40：

例如 `/subdir` 映射到一个真实目录时，第一条检查得到 `exists=True`，所以缺失规则不匹配；第二条得到 `isfile=False`，所以文件规则也不匹配。循环继续到此规则。它不再检查目录属性，职责是确保所有剩余路径都进入统一错误出口。

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `case_always_fail.test`、`case_always_fail.act`；原行 33–40；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L33-L40)。

#### 完整原文

```python
class case_always_fail(object):
    '''Base case if nothing else worked.'''

    def test(self, handler):
        return True  # 教学注释：无条件匹配，依靠列表顺序保证它最后运行。

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))  # 教学注释：把未识别目标送回共同错误出口。
```

#### 原行 33–40：恒真条件为什么必须最后

原行 33–34 定义兜底类与说明。原行 36–37 的 `return True` 不查看 `handler`，所以无论收到什么输入都会匹配；原行 39–40 的动作抛出带请求路径的 `ServerException`。这解释了为什么往规则表追加新规则时必须插在 `case_always_fail()` 前面，否则兜底会先被选中。

对 `/subdir`，循环得到 `False`、`False`、`True`。第三个 `act` 抛出的文字是 `Unknown object '/subdir'`，异常到达 `do_GET` 后由错误处理器显式转成 404。若把此对象移到第二位，那么普通 `/plain.html` 会在测试文件规则前就命中恒真条件，同一个 `/plain.html` 也会收到错误页；这不是性能差一点，而是规则结果变错。

它的输入输出契约有意很小：判断方法总返回真，动作不会正常返回。更精细的目录首页规则应放在普通文件规则之后、此兜底之前。固定提交的独立 `server-index-page.py` 正是这样注册一个目录规则；对应真实接线在原行 65–68，规则类在原行 33–44，后面第八章会用 `/guide` 跟一次具体调用。

#### 代入 `/subdir`：测试为真不等于动作正常返回

前两条规则结果是 `False`、`False` 后，兜底对象的 `test(handler)` 返回 `True`。`do_GET` 因此调用 `case_always_fail.act(handler)`；这个 action 没有正常的 return，直接抛 `ServerException("Unknown object '/subdir'")`。控制越过循环底部，不会执行 `break`，随后由 `do_GET` 的 `except` 调用错误处理。要区分两处结果：兜底的 `test` 正常返回布尔 `True`，action 则抛异常；`test` 的真值本身没有产生 404。

#### 设计与接入：兜底为什么必须最后

兜底只知道“前面的规则都没有处理”，所以表的顺序就是它的输入条件。若把它插在普通文件 case 前，`/plain.html` 也会由它匹配并抛错，后面的读取动作永远到不了；若新增目录首页 case，则应在普通文件规则后、兜底前注册。只定义新类但没有把实例放入 `Cases`，`do_GET` 不会调用它；把注册放在兜底之后也等同于没接入。若某个新 action 正常返回，循环需要清楚知道何时停止，当前消费者依靠 `break`。

### 5.5 在处理器类建立共享规则表和错误页模板

#### 实际问题、类体执行时机与值的归属

三个 case 类已经定义，下面的类体可以创建实例并保存它们。错误模板也属于类级数据：它提供正文文字，但不负责发送响应。原行 44–62：

解释器执行 `class RequestHandler(...)` 时会运行缩进的类体。它不是每来一条请求就重新执行一次；类属性 `Cases` 和 `Error_Page` 在模块加载时创建，之后被这个类的所有实例查找。当前请求的 `self.path`、`self.full_path` 则不放进类属性，而是在 handler 实例上。`Error_Page` 是数据模板，最终调用 `.format(...)` 的位置在原行 92，网络输出要等原行 93 和 `send_content`。

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `RequestHandler`、`Cases`、`Error_Page`；原行 44–62；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L44-L62)。

#### 完整原文

```python
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''
    If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed.
    '''

    Cases = [case_no_file(),
             case_existing_file(),
             case_always_fail()]  # 教学注释：类定义执行时创建三个共享的 case 实例。

    # How to display an error.
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """
```

#### 原行 44–62：继承、共享规则对象和待填模板

原行 44 声明项目类继承标准库的 `BaseHTTPRequestHandler`；标准库 `TCPServer` 接受连接后，基类处理该连接上的 HTTP 读取、解析和方法分派，项目只覆写自己的处理行为。原行 45–48 是整个类的 docstring，概括路径映射和错误页职责。

原行 50–52 在类体执行时分别调用三个类名，结果是三个实例，按“缺失、普通文件、兜底”放入列表。列表是类属性；每条连接的处理器通过 `self.Cases` 找到同一张表。case 实例没有存入某个用户的路径，而是由每次 `test(handler)`、`act(handler)` 调用接收当前处理器。

原行 54 是原注释。原行 55 将多行字符串存入 `Error_Page`；开引号后紧邻的反斜线去掉字符串开头的换行。原行 56–62 依次构成 HTML 的 `html`、`body`、`h1`、`p` 和闭合标签，`{path}` 与 `{msg}` 留待 `.format(...)` 填值。模板只产生字符串；它没有 `send_response`、状态码或网络写操作。两个占位符会原样插入，没有 HTML 转义。

遇到一次缺失请求时，所有 handler 实例都读取同一份 `Cases` 和模板，但只有当前 handler 带着 `self.path='/missing.html'`。稍后 `.format(path=self.path, msg=msg)` 产生一份新的错误正文字符串；模板本身不变。共享常量/规则和每请求路径分别放在类与实例上，避免把某个访问者的路径写进全局共享对象。

当前代码没有把格式化结果写回模板。若显式执行 `RequestHandler.Error_Page = formatted`，就会改共享类属性，后续 handler 都会读到这个新模板；若执行 `handler.Error_Page = formatted`，则会在这个实例上建立同名属性，遮住类属性，只影响该 handler。模板中的缩进空白会保留在字符串里，HTML 解析会忽略多数标签间空白，但错误文字并未经过 HTML 转义。要改错误页内容，应检查 `.format` 的实际消费者；只改标签不会改变状态码，状态码仍由调用 `send_content` 的参数决定。

#### 模板实参怎样变成一次请求的正文

以缺失目标为例：`self.path` 是 `/missing.html`；原行 18 已把它格式化成 `'/missing.html' not found` 并放在 `ServerException` 对象里。原行 78 捕获的 `msg` 是这个异常对象，不是提前转成的普通字符串。原行 92 执行 `Error_Page.format(path=self.path, msg=msg)` 时，`{path}` 收到请求路径，`{msg}` 按默认字符串转换显示异常文字；新字符串的标题是 `Error accessing /missing.html`，正文消息是 `'/missing.html' not found`。格式化只新建一份正文，不改变模板或 `self.path`；原行 93 才将正文和 404 交给发送方法。

#### 共享类属性和请求实例属性怎样区别

`Cases` 列表和 `Error_Page` 字符串都是 `RequestHandler` 的类属性，所有 handler 实例按属性查找都能读到它们。三个 case 对象在类体执行时创建一次；原模板字符串不可变，`.format(...)` 返回新字符串，所以每个错误正文不会回写共享模板。若运行时执行 `handler.Error_Page = '...'`，Python 会在该 handler 的实例属性中建立同名值，遮住类属性；这不会自动改其他 handler。若修改 `RequestHandler.Error_Page` 则改的是类级值，后续所有实例都会查到它。类似地，原地向 `RequestHandler.Cases` 追加会影响共享列表，而 `handler.Cases = [...]` 会为该实例建立遮蔽值。当前代码没有做这些赋值；这是维护或扩展时必须区分的接线点。

### 5.6 `do_GET` 用当前目录和请求目标选择第一条规则

#### 实际触发、请求输入与准备好的状态

标准库把 `GET` 分派给这个方法时，`self` 就是刚为连接创建的处理器实例，已经带有 `self.path`。在假设工作目录 `/work/500lines/web-server/code/03-handlers` 和请求目标 `/plain.html` 下，方法要先形成磁盘路径，再按有序规则决定后续调用。原行 64–79：

对 `GET /plain.html HTTP/1.1`，标准库先把方法写入 `self.command='GET'`、把目标写入 `self.path='/plain.html'`；本方法不再拆请求行。类级规则表从 `self.Cases` 取得，路径字段属于这个 handler 实例。请求方法来源于标准库的分派，项目可以通过同一个实例的 `self.path` 与继承字段继续处理。

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `RequestHandler.do_GET`；原行 64–79；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L64-L79)。

#### 完整原文

```python
    # Classify and handle request.
    def do_GET(self):
        try:

            # Figure out what exactly is being requested.
            self.full_path = os.getcwd() + self.path  # 教学注释：保存本次处理器所用的完整路径。

            # Figure out how to handle it.
            for case in self.Cases:
                if case.test(self):  # 教学注释：把当前 handler 显式传给 case 的判断方法。
                    case.act(self)  # 教学注释：执行首个匹配规则的动作。
                    break  # 教学注释：动作正常返回后不再检查后续规则。

        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)  # 教学注释：把普通异常交给统一错误页处理。
```

#### 原行 64–79：赋值、扫描和异常接收

原行 64 的注释说明分类与处理目的。原行 65 定义 `do_GET(self)`；此处 `self` 是处理器，不是刚才 case 方法里的 case `self`。原行 66 的 `try` 包住路径赋值和整个规则循环。

原行 69 先读进程当前工作目录，再与标准库保存的请求目标拼接：`'/work/500lines/web-server/code/03-handlers' + '/plain.html'` 得到 `'/work/500lines/web-server/code/03-handlers/plain.html'`，存到此处理器实例的 `full_path`。它没有用脚本文件所在目录，也没先解析查询串或规范化 `..`；路径来自当前工作目录和原始请求目标。

原行 72 依次从类级 `Cases` 取规则。原行 73 把当前处理器作为实参交给 `test`；成功场景中缺失规则返回 `False`，文件规则返回 `True`。原行 74 调用文件 case 的 `act`，它再调用 `handle_file`；原行 75 只有在该动作正常返回后才执行，离开循环。原行 77 是原注释。原行 78 捕获 `Exception` 及其子类，将异常对象绑定到 `msg`；原行 79 调用统一错误页。这个宽泛捕获也可能把项目程序错误显示成 404，不能把它读成只捕获“文件不存在”。

这一行里的赋值只保存路径字符串，并没有检查路径安全或打开文件。对 `/plain.html`，循环的布尔值顺序是 `False`、`True`；文件动作正常结束后才走到 `break`。对缺失的 `/missing.html`，第一条测试就是 `True`，动作抛 `ServerException`，所以不经过 `break`；异常直接到 `except`。对存在的目录，前两条是 `False`、`False`，最后的恒真规则抛异常。相同循环因此同时处理正常与未匹配目标，但两种失败进入错误出口的时刻不同。

循环调用点就是这份规则表的接线：要新增行为，必须让新的 case 实例进入 `Cases`，并确保放在兜底之前；只定义一个类不会让服务器扫描到它。所有动作都同步执行，`case.act(self)` 返回后才看 `break`；这里没有后台任务或自动队列。想单独处理查询参数、目录首页或 HTTP 方法，都需要具体改它们的真实入口和消费点。

#### 按小行组追踪状态变化

**原行 69：建立每请求字段。** `os.getcwd()` 读的是进程当前工作目录；`self.path` 是标准库刚解析出的请求目标。两者是字符串，`+` 按字符顺序拼接成磁盘路径，不执行路径规范化或 URL 解码。结果写入当前 handler 的 `full_path`，后续 `case.test(self)` 和 `case.act(self)` 都从传入的 handler 读取同一个值。把它存到 handler 的效果，是让多个规则共享一份本请求路径而不用重复组装；这是从调用接口看到的好处，不替原作者声称主观动机。可直达 [原行69](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L69)。

**原行 72–73：循环和条件的值消费者。** `for case in self.Cases` 把列表里的已有对象依次绑定到局部变量 `case`；它没有在这里创建对象。表达式 `case.test(self)` 中外层 `self` 是 handler，方法绑定把 case 对象交给 `test` 的第一个参数 `self`，括号里的 handler 则成为显式参数 `handler`。`test` 返回的布尔值由 `if` 消费：`False` 时跳过缩进动作并进入下一轮，`True` 才进入动作。这次成功输入的结果是 `N.test(H)=False`、`E.test(H)=True`。调用现场见 [原行72–73](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L72-L73)。

**原行 74–75：副作用与退出时机。** 文件 case 的 `case.act(self)` 调用 `handle_file(full_path)`，这个调用值不被赋给变量，也不由 `do_GET` 检查；它的意义是读文件并尝试写响应。只有方法正常返回，解释器才走到 `break`，由它结束最近的 `for`。若去掉 `break`，成功读取 `/plain.html` 后循环还会到恒真兜底；兜底抛错，外层 except 会再尝试写 404。此时前一个 200 响应已开始，不能再得到一条保证有效的单一响应。动作、`break` 的精确顺序见 [原行74–75](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L74-L75)。

**原行 78–79：异常返回给谁。** `except Exception as msg` 把 `try` 中抛出的普通异常对象绑定到局部名 `msg`；`handle_error(msg)` 是同一 handler 上的方法调用。它不显式返回内容，因此若成功写错误响应，`do_GET` 也在 except 末尾隐式返回 `None`。若 `handle_error` 自己写响应时再抛 `IOError`，它发生在当前 except 的处理体内，不会被同一个 `try` 重复捕获；标准库的外层服务器错误处理才会看到未处理异常。宽泛异常边界的源码在 [原行78–79](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L78-L79)。

### 5.7 `handle_file` 读完文件后才开始写成功响应

#### 调用现场、输入来源与错误范围

当前文件 case 调用 `handle_file(full_path)`，传入值为 `'/work/500lines/web-server/code/03-handlers/plain.html'`。这里先从磁盘读取，再把字节交给输出方法。需要特别留意：`send_content` 也在此 `try` 块中。原行 81–88：

上游是 `case_existing_file.act(handler)`，它把 `handler.full_path` 作为唯一实参传来；本方法不接收 URL，也不重新定位工作目录。`content` 是一次 `read()` 得到的 Python 2 字节串，不是文件名、响应对象或逐块生成器。下游 `send_content` 消费这份完整字节串。

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `RequestHandler.handle_file`；原行 81–88；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L81-L88)。

#### 完整原文

```python
    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)  # 教学注释：省略状态实参，使用默认 200。
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)  # 教学注释：文件输入输出异常时尝试发送项目错误页。
```

#### 逐行读：参数、缩进、作用域和资源边界



`def handle_file(self, full_path)` 中，`self` 是当前 `RequestHandler` 实例，`full_path` 是调用方传来的磁盘路径。`try` 覆盖文件读取和后续响应发送。`with` 管理 reader 的文件资源何时关闭，不会创建新的局部变量作用域；`content` 是读出的独立字节串，离开 `with` 后仍可使用；`reader` 仍绑定已关闭的文件对象，再调用它的 `read()` 会失败。

原行 83 的 `'rb'` 中 `r` 表示读取，`b` 表示二进制；这里要保留原文件字节，不让文本模式替换换行或隐式解码。`as reader` 把 `open` 的返回对象命名为 `reader`。原行 84 调用无参数 `.read()`，一次把当前位置直到文件尾的全部字节取出，赋给函数局部变量 `content`。离开 `with` 后 reader 关闭，随后原行 85 才调用 `send_content`。成功调用省略第二个参数，所以按方法签名取默认 `200`。原行 86 的 `except IOError as msg` 把异常对象先绑定到局部名 `msg`；下一行重新给同名局部变量赋格式化后的字符串。`self.path` 是标准库解析出的 URL 请求目标，`full_path` 是传入的磁盘路径，两者不是同一种路径。

原行 86 的 `except IOError as msg` 同时覆盖文件打开、读取和原行 85 的响应发送。若 `open` 失败，文件对象尚未创建；若 `read` 失败，`with` 先关闭已打开的 `reader`，之后再进入错误分支。原行 87 的 `.format(self.path, msg)` 令 `{0}` 取请求目标 `self.path`，`{1}` 取捕获到的 `IOError` 对象并转成错误文字；返回的普通字符串重新赋给 `msg`，原行 88 再把它交给 `handle_error` 并尝试发送 404。若 `send_content` 写出状态、头部或正文时抛出 `IOError`，同一个分支却会把网络错误误标成“文件不可读”，再尝试写错误响应。故障前可能已经交给连接输出流 `200` 状态行或部分头/正文；再次写 404 不能撤回它们，也不能保证连接仍可写。这个实现没有分开磁盘读错误与网络写错误，不能承诺该分支最终让浏览器收到 404。

#### 代入输入看正常返回和两种 `IOError`

成功时，case 传入 `'/work/500lines/web-server/code/03-handlers/plain.html'`；`open` 返回文件对象，`read()` 得到 116 字节，其中 9 个 LF 换行，`with` 关闭文件，然后 `send_content` 尝试写成功响应。方法没有 `return` 语句，所以若发送方法正常返回，`handle_file` 也隐式返回 `None`。此值依次经过 `case_existing_file.act` 回到 `do_GET`；动作调用正常结束，执行原行 75 的 `break`。

如果 `open` 抛 `IOError`，文件对象尚未创建；如果 `read` 抛 `IOError`，解释器先离开 `with` 并关闭已打开的文件，再进入 `except`。`handle_error(msg)` 若完成，`except` 到末尾自然返回 `None`，因此这次读取失败仍会从 `act` 正常返回并到达 `break`。若异常发生在 `send_content`，已写出的状态行或头部可能是 200；同一 `except` 会把网络错误误称为文件不可读并尝试第二次发送，结果不能保证变成完整 404。

`with` 块里只包含打开与读取。若 `open` 成功、`read` 失败，离开块时 Python 仍关闭 reader，然后才执行 `except`；若读取成功，关闭也发生在 `send_content` 之前。因此文件资源不需要等网络发送结束才释放。对原始页面，读取到的文件是 116 字节，其中 9 个 LF 换行；发送长度在下游重新从这份 `content` 计算，不从文件名或字符数猜测。

#### 为什么整份读取，以及要改哪些接线

当前小文件例子一次 `read()` 后就能按最终字节数生成 `Content-Length`，且读完即关闭磁盘文件，再开始网络输出。一个具体替代是分块读取，但那会改变当前调用契约：`content` 不再是一份完整字节串，必须重新决定是先知道长度、分块发送还是使用连接关闭作为结束信号，并审视持久连接。另一个局部替代是只让磁盘 `open/read` 落在 `try` 内、将 `send_content` 移到错误捕获之外；这样网络写错误就不会被误包装成“文件不可读”。两种改动都要从本方法的读/发送边界开始，并核对调用者仍能理解动作正常返回还是抛错。

这段实现把“读盘错误”和“网络写错误”放进同一个 `try`，省代码但误报。一个具体替代是先单独捕获打开/读取异常，再在 `try` 外发送成功内容；这样写响应失败不会再次被包装成文件读取失败。大文件则不能简单把 `reader.read()` 改成循环就结束设计：还需决定响应长度、发送终止条件和连接复用规则。当前代码选择小文件全读，推理简单，代价是内存占用随文件大小增长。

### 5.8 错误路径显式选 404，发送方法负责共同格式

#### 调用现场、两个方法各自接收什么

对缺失请求，`self.path` 是 `/missing.html`，`msg` 是 `do_GET` 捕获到的 `ServerException` 异常对象；只有 `handle_error` 调用模板 `.format(...)` 时它才转成页面文字；对文件读取失败，`msg` 已在 `handle_file` 原行 87 中格式化为包含底层 `IOError` 文字的普通字符串。`handle_error` 负责把值填入 HTML 并选择 404；`send_content` 负责按统一次序写状态、头部、空行和正文。成功读取的另一个调用者只传正文，因此共用同一个发送方法但得到默认 200。

`do_GET` 的缺失与兜底规则都到达 `handle_error`；`handle_file` 的输入错误也尝试到达这里。它先创建错误正文，再将状态选择交给同一发送函数。原行 90–93：

**源码定位：** `web-server/code/03-handlers/server.py`；符号 `RequestHandler.handle_error` 原行 90–93，以及 `RequestHandler.send_content` 原行 95–101；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[错误处理原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L90-L93)、[响应发送原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L95-L101)。
```python
    # Handle unknown objects.
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)  # 教学注释：第二个位置实参覆盖默认成功状态。
```

#### 逐行读：格式化如何把异常变成页面文字

原行 90 是原注释。原行 91 的方法参数 `msg` 是调用方传来的异常对象或错误文字；`self` 仍是处理器实例。原行 92 的 `.format(path=self.path, msg=msg)` 使用关键字实参把值映射到同名花括号占位符，得到一整段 HTML 字符串；`path=self.path` 是传参语法，不是在这里改写对象字段。原行 93 把该正文与整数 `404` 一起传给 `send_content`。

#### 代入缺失和读取错误，看调用边界

缺失路径时，`case_no_file.act(handler)` 抛出 `ServerException`；它传到 `do_GET` 的 `except`，这里再以异常对象调用 `handle_error(msg)`。读取失败时，`handle_file` 已先把异常格式成文字再调用 `handle_error`。两种输入最终都使 `{path}` 取本次 `self.path`，`{msg}` 由 `.format` 转成可插入模板的文字。此时 `content` 还只在内存里，直到 `send_content` 开始写响应。模板没有对 `path` 或 `msg` 做 HTML 转义，含标记字符的输入会原样进入 HTML；这个结论来自此处格式化与输出的实际连接。

成功与失败使用同一输出函数，调用点传不同的状态。原行 95–101：

#### 完整原文

```python
    # Send actual content.
    def send_content(self, content, status=200):
        self.send_response(status)  # 教学注释：由标准库写状态行及其标准响应头。
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))  # 教学注释：把正文的字节长度写成头部文字。
        self.end_headers()  # 教学注释：输出空行，结束响应头部。
        self.wfile.write(content)  # 教学注释：把正文交给已接受连接的输出流。
```

#### 逐行读：默认值和状态由调用点选择

原行 95 的原注释是 `# Send actual content.`，说明方法要把实参正文写出。原行 96 的 `content` 是待发正文，调用时 `self` 已绑定为当前 handler；`status=200` 的等号为默认参数语法，不是发送动作。成功文件路径调用 `send_content(content)`，因此 `status` 取 200；错误方法调用 `send_content(content, 404)`，第二个位置实参让 `status` 取 404。调用者明确选择状态，`send_content` 不根据正文文字猜状态。

原注释 `# Send actual content.` 与四个行尾教学注释都留在代码块里：后者明确标出标准库状态/响应头、空行和连接输出流，并非固定版本源码注释。原行 97 调用从基类继承的 `send_response`，先写状态行以及标准 `Server`、`Date` 头。原行 98 的 `send_header` 逐项写项目固定的 `Content-type: text/html`。原行 99 先让 `len(content)` 数正文长度，再由 `str(...)` 转成头部可写的十进制文本；成功正文是 Python 2 字节串，因此这里数的是字节。原行 100 通过 `end_headers()` 写头部与正文之间的空行。原行 101 才把 `content` 交给该连接的 `wfile`；**写入调用返回不代表对端已收到这些字节**。

#### 代入一条响应：状态行、长度和发送失败

把 `/missing.html` 代入：调用方交来错误 HTML 字符串和整数 `404`，所以输出形状是 `HTTP/1.0 404 Not Found` 状态行，接着是标准 `Server`、`Date`，再是 `Content-type: text/html` 与 `Content-Length: <len(content)>`，然后一个空行，最后是错误 HTML 正文。`<len(content)>` 表示对这次格式化后正文调用 `len` 得到的十进制值；这里不预造日期头或错误页总长度。成功文件分支省略状态实参，按签名取 200。顺序不能交换，因为接收方先要知道响应状态和头部，空行之后才是正文。

`send_response`、两个项目 `send_header` 调用、`end_headers` 和最后的 `wfile.write` 按顺序调用；`send_response` 内部还会写状态行并调用 `send_header` 写 `Server`、`Date`。若其中任一步抛 `IOError`，执行不会到达后续步骤；已经交给输出流的字节不能撤回。`handle_file` 会捕获写出时的 `IOError` 并尝试错误页，但第二次发送也可能失败，因此实际可见结果只在整条写出成功时才是完整的 404 或 200。修改状态格式、头部字段或正文格式时，应检查本方法的顺序调用及两个调用者：成功读文件的 `handle_file` 和错误页面的 `handle_error`。

Python 2.7.18 的 `send_response` 直接把状态行写到 `wfile`，再用 `send_header` 写 `Server`、`Date`；这里没有 Python 3 的 `headers_buffer` 暂存机制。`send_content` 也没有先组装完整响应再一次性提交，因此在头部或正文写到一半时失败，连接上可能已有部分 200 响应。再次调用错误出口不能收回已写字节，也不能保证完整 404。若将来增加不同文件类型，要改 `Content-type` 的输入决策；若改变正文编码，则长度必须继续对最终待发字节求值。

### 5.9 主入口把处理器类交给监听服务器

#### 启动触发、参数和值的含义

所有规则和方法已经定义，脚本作为程序运行时才会执行入口。这里的第二个实参是类，不是预先创建的 handler 对象。原行 105–108：

文件直接作为脚本执行时，解释器令 `__name__` 等于 `'__main__'`，于是入口成立；若其他模块导入此文件，定义可被加载，但不会因此启动监听循环。本段把绑定地址和端口传给标准库 `HTTPServer`，并把 `RequestHandler` 类交给它。服务器实例保存监听 socket 和处理器类；当前没有任何连接级 handler，也没有读取 `plain.html`。

**源码定位：** `web-server/code/03-handlers/server.py`；模块入口 `if __name__ == '__main__'`；原行 105–108；固定提交 `fba689d101eb5600f5c8f4d7fd79912498e950e2`；[不可变原文](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py#L105-L108)。

#### 完整原文

```python
if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
```

#### 逐行读：入口条件、地址值和类实参

原行 105 检查 Python 设置的模块名是否为 `'__main__'`；直接运行脚本时成立，被导入时不执行此入口。原行 106 的圆括号创建二元组，第一项是空主机文字、第二项是端口整数 `8080`。原行 107 创建标准库 HTTP 服务器；`RequestHandler` 作为类交给服务器保存，连接到来后才实例化。原行 108 调用 `serve_forever()`，让进程持续接受和处理连接，直到被停止。入口没有读 `sys.argv`，所以给脚本附加目录参数不会改变这里的主机、端口或 `os.getcwd()`。

第 106 行的 `''` 不是“仅本机回环地址”：在这个 IPv4 `HTTPServer` 中它表示任意本地 IPv4 接口。用户可用 `127.0.0.1` 在同一台机器访问，但服务器绑定范围仍覆盖其他可用接口。端口 `8080` 若已被占用，构造服务器时绑定会失败，`serve_forever()` 也就不会开始。工作目录若不是源码旁边的 `03-handlers`，后续拼出的 `full_path` 会指向另一位置；脚本路径本身不会替代当前工作目录。

#### 调用后接什么：类由谁保存，连接对象何时创建

`BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)` 消费两个实参：`('', 8080)` 用于绑定监听地址，第二实参是类对象 `RequestHandler`。它不是 `RequestHandler()` 的结果；若在这里先手工建一个实例再传入，类型契约就错了，因为标准库后续要对类调用 `RequestHandler(request, client_address, self)`，按每条已接受连接建立 handler。启动这一刻只有服务器与类级 `Cases` 已存在，还没有连接级 `self.path` 或 `self.full_path`。

`serve_forever()` 进入标准库等待连接的循环。若端口 8080 已被占用，失败发生在构造器绑定阶段，异常沿入口调用栈返回，后面的 `serve_forever()` 不会执行；若绑定成功，循环才等待连接。`''` 在此 IPv4 服务器中表示所有本地 IPv4 接口，不等于 loopback。真实上游是脚本的 `__main__` 入口，接下来由 `accept()` 和 `finish_request()` 创建 handler；真实下游是第六章的连接/请求处理机制，以及第八章的工作目录和浏览器操作说明。若改变主机或端口，修改这里的 `serverAddress`；若改变处理规则，修改传入的 handler 类定义及类级 `Cases`，而不是在这四行创建 handler 实例。


## 6. 关键机制与官方资料解读

本章标准库片段来自 CPython 官方仓库固定标签 `v2.7.18`，每段均在代码前列出模块、符号、原行和不可变链接；解释依据同标签的实现与 `.rst` 文档。它们不是 AOSA 示例代码的一部分。CPython 源码的许可应以该标签随附的[官方 LICENSE](https://github.com/python/cpython/blob/v2.7.18/LICENSE)为准；本篇末尾的 AOSA MIT 说明只对应 AOSA 的示例文件，不覆盖这里摘录的标准库代码。

### 监听服务器如何变成一次连接处理

项目入口调用 `BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)`，并传入处理器**类**。CPython 2.7.18 的 `HTTPServer` 继承 `SocketServer.TCPServer`；TCP server 构造时创建 IPv4 stream socket，按 `serverAddress` 绑定并监听。父类保存 `RequestHandlerClass`，也就是 `RequestHandler` 类，而不是一份 handler 实例。可核对 [`HTTPServer` 定义](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L102-L111)、[`TCPServer.__init__`](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L413-L424) 与 [`BaseServer.__init__`](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L201-L206)。

`serve_forever()` 等待监听 socket 可读；就绪后 `_handle_request_noblock()` 调用 `get_request()`，而 `TCPServer.get_request()` 实际用 `accept()` 得到一条已连接 socket 和客户端地址。默认 `process_request()` 同步调用 `finish_request()`；后者以这条 socket、客户端地址和服务器对象构造 `RequestHandlerClass`。因此请求处理不是服务器直接执行 `do_GET`，也没有自动为每个客户端创建线程。循环与接受链可核对 [`serve_forever` / `_handle_request_noblock`](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L216-L298)、[`process_request` / `finish_request`](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L315-L334) 和 [`get_request`](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L461-L467)。

#### 从入口实参到监听 socket：标准库原文

先看父类保存入口传入的两个对象。源码定位：CPython 2.7.18 `Lib/SocketServer.py`，`BaseServer.__init__` 原行 201–206；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L201-L206)。
```python
    def __init__(self, server_address, RequestHandlerClass):
        """Constructor.  May be extended, do not override."""
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False
```

原行 201 的两个参数正对应项目传入的 `('', 8080)` 和 `RequestHandler` 类。原行 203 把地址值保存在服务器实例；原行 204 保留类对象，尚未调用它，因此这里不会创建 handler。原行 205、206 建立循环停止与同步状态，服务循环稍后会读写这些状态。构造参数的大小写命名 `RequestHandlerClass` 提醒读者它是类，不是 handler 当前实例。

原行 205 的 `threading.Event()` 建立线程间可观察的信号对象；`__is_shut_down` 以至少两个下划线开头、但不以两个下划线结尾；类定义会把这种名字改写成带类名的形式，例如 `_BaseServer__is_shut_down`，以减少子类意外同名覆盖。`__init__` 两端都有双下划线，是特殊方法，不按这条规则改写。这个属性表示内部状态，不是 HTTP 头字段。原行 206 的 `__shutdown_request` 是另一个内部布尔标记。`serve_forever()` 开始时对 Event 调用 `clear()`，退出的 `finally` 中调用 `set()`；它用这个信号表示服务循环是否已经结束。当前项目只启动循环，没有另建线程调用 `shutdown()`，所以这两个值属于标准库生命周期机制，不是处理一个 GET 的业务字段。

再看 TCP 服务器如何处理同一组实参。源码定位：`TCPServer.__init__` 原行 413–424；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L413-L424)。
```python
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        """Constructor.  May be extended, do not override."""
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        if bind_and_activate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise
```

原行 415 先用继承来的父类初始化保存地址与类；它把当前 TCPServer 实例作为父类方法的 `self`。原行 416–417 根据类属性 `address_family` 和 `socket_type` 创建监听用 socket，HTTPServer 的 IPv4 与 stream 类型定义在其继承关系中。原行 418 允许内部调用者选择只构造、不绑定；项目省略第三个参数，使用 `True`。原行 420–421 依次绑定地址、开始监听；`server_activate()` 的 TCPServer 实现会调用 `listen()`。若绑定或监听抛出异常，原行 422–424 先关闭已建 socket，再用裸 `raise` 把原异常继续交给入口调用者；没有可用监听实例时，后面的服务循环不会运行。

`def __init__(self, ..., bind_and_activate=True)` 定义构造方法，类调用自动把新服务器实例绑定到第一个参数 `self`；调用方这次没有给第三个参数，所以 `True` 生效。文档字符串中的“May be extended, do not override”是维护说明，提醒子类扩展时保留构造约定，不是运行指令。`BaseServer.__init__(self, ...)` 是显式父类调用，传入同一个 TCPServer 实例，让父类把地址与 handler 类保存在这个对象上。裸 `except:` 捕获绑定/监听中途的异常；单独的 `raise` 会把当前异常继续抛给构造调用者，而不是转成启动成功。

循环如何从监听 socket 到一个连接，关键段落如下。源码定位：`BaseServer.serve_forever` 原行 216–239、`_handle_request_noblock` 原行 280–298；[固定版本原文一](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L216-L239)、[固定版本原文二](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L280-L298)。
```python
    def serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.

        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """
        self.__is_shut_down.clear()  # 教学注释：重置“服务循环已结束”信号。
        try:
            while not self.__shutdown_request:  # 教学注释：只要没有收到停止标记，就继续轮询。
                # XXX: Consider using another file descriptor or
                # connecting to the socket to wake this up instead of
                # polling. Polling reduces our responsiveness to a
                # shutdown request and wastes cpu at all other times.
                r, w, e = _eintr_retry(select.select, [self], [], [],
                                       poll_interval)  # 教学注释：监视监听socket是否可读。
                # bpo-35017: shutdown() called during select(), exit immediately.
                if self.__shutdown_request:  # 教学注释：select等待期间也可能收到停止请求。
                    break
                if self in r:  # 教学注释：r中包含监听对象才有连接可接受。
                    self._handle_request_noblock()
        finally:  # 教学注释：正常退出或异常退出都会整理停止状态。
            self.__shutdown_request = False
            self.__is_shut_down.set()  # 教学注释：通知等待方循环已结束。

    def _handle_request_noblock(self):
        """Handle one request, without blocking.

        I assume that select.select has returned that the socket is
        readable before this function was called, so there should be
        no risk of blocking in get_request().
        """
        try:
            request, client_address = self.get_request()
        except socket.error:  # 教学注释：accept阶段取连接失败时结束这次尝试。
            return
        if self.verify_request(request, client_address):  # 教学注释：基类默认允许该连接。
            try:
                self.process_request(request, client_address)
            except:  # 教学注释：处理器构造/处理异常交给服务器级错误钩子。
                self.handle_error(request, client_address)  # 教学注释：这是BaseServer的错误处理方法。
                self.shutdown_request(request)
        else:  # 教学注释：校验拒绝时不创建handler，直接关闭连接。
            self.shutdown_request(request)
```

#### 逐行读：等待、就绪判断和停止信号

这里展示的是两个不相邻方法的原行组合；省掉的只是它们之间不参与本课主路径的 `shutdown()` 和 `handle_request()` 定义。`serve_forever(poll_interval=0.5)` 的默认实参是半秒轮询间隔，不是请求处理时限。`clear()` 把“已结束”事件重置；`while not self.__shutdown_request` 每次先读停止布尔值，值为假才继续循环。源码保留的 `XXX` 注释说明轮询会延迟响应 shutdown 并浪费空闲 CPU；这一注释指出权衡，不是额外执行语句。

`r, w, e = ...` 是把三个返回值一次解包到可读、可写、异常就绪列表。此处只关心 `r`：`[self]` 把监听服务器放入待观察对象列表，两个 `[]` 表示本次不监视可写或异常对象，末尾 `poll_interval` 作为超时。`select.select` 等待期间若被系统信号打断，`_eintr_retry` 会在系统错误标记 `EINTR`（interrupted system call，即系统调用被信号打断）时重试；其他错误仍抛出。返回后再次检查 `__shutdown_request`，处理“等待期间有人请求停止”的情况。只有 `self in r` 才调用 `_handle_request_noblock()`；这代表监听 socket 可读、有连接可接受，不代表 HTTP 请求正文已解析。

`finally` 不论循环正常结束还是循环体抛异常都会执行：先把停止请求标记复位，再 `set()` Event，通知等待关闭完成的调用者。这里的双下划线字段是服务器内部的协调状态；项目 handler 的 `self.path` 与它们无关。`w` 和 `e` 被解包但本方法不再使用，因为当前实现只注册监听 socket 的可读事件。

#### 逐行读：接受失败、校验和两层错误处理

`get_request()` 的返回值被拆成新连接 `request` 和客户端地址 `client_address`。若接受连接抛 `socket.error`，`except` 后的裸 `return` 只结束这一轮；没有 handler 可创建，也没有项目错误页可写。`verify_request` 是服务器的过滤钩子，核对本标签源码可见 `BaseServer.verify_request` 默认直接返回 `True`，所以本课不覆写它时继续往下走；子类可以改成拒绝，此时 `else` 分支关闭连接。

验证通过后，`process_request` 默认同步进入 handler 构造。里面若抛异常，这里的裸 `except` 把它交给 `BaseServer.handle_error(request, client_address)`，再调用 `shutdown_request(request)` 收尾。这个 `handle_error` 是服务器实例的方法，接收 socket 和地址；它不是 AOSA 的 `RequestHandler.handle_error(msg)`，后者接收项目错误值并尝试写 HTML 404。二者同名但对象、参数和职责不同。若验证拒绝，则不进入错误钩子，只关闭连接。`request` 是 accept 得到的已连接 socket，不是监听 socket，也不是解析后的 HTTP 请求对象。
这一步的类调用在原文中很短，值得直接读。源码定位：`BaseServer.process_request`、`BaseServer.finish_request` 原行 315–334；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L315-L334)。
```python
    def process_request(self, request, client_address):
        """Call finish_request.

        Overridden by ForkingMixIn and ThreadingMixIn.

        """
        self.finish_request(request, client_address)
        self.shutdown_request(request)

    def server_close(self):
        """Called to clean-up the server.

        May be overridden.

        """
        pass

    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(request, client_address, self)
```

#### 逐行读：处理请求与 `pass` 的边界

`process_request` 把 accept 得到的 `request` 和 `client_address` 原样转给 `finish_request`，然后调用 `shutdown_request(request)`；该默认实现会结束并关闭这条请求连接。`finish_request` 最后一行才用保存的 `RequestHandlerClass` 调用类，三个位置实参依次是连接 socket、客户端地址和服务器对象。Python 的类调用创建 handler 实例并运行初始化；它不把 handler 返回值保存下来，因为处理动作在构造调用期间同步完成。

代码中间的 `server_close()` 是另一个清理钩子，只有服务器对象被显式关闭时由其调用链使用；它不夹在这里的单请求 `process_request` 路径里。基类实现正文 `pass` 表示没有通用动作，具体 server 子类可覆写；它与 `shutdown_request(request)` 关闭已接受连接不是同一清理。文档字符串中的“May be overridden”提示扩展点，不是一次调用。`process_request` 文档中的 `ForkingMixIn`、`ThreadingMixIn` 表示混入类可以覆写此方法改变同步处理方式；本课传入的是普通 `HTTPServer`，因此这里沿用顺序调用。

Python 2.7.18 的官方 [`socketserver` 文档](https://github.com/python/cpython/blob/v2.7.18/Doc/library/socketserver.rst)也把这个组合写成三步：创建并传入 handler 类、实例化 server、调用 `serve_forever()`；它说明 `TCPServer` 默认同步处理，并由 `finish_request` 实例化 handler。这里的源码将文档概览具体化为项目地址和类实参。

#### `accept()` 返回的是什么：标准库原文

从服务器方法看，二元组由 `TCPServer.get_request()` 原样交出。源码定位：CPython 2.7.18 `Lib/SocketServer.py`，`get_request` 原行 461–467；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L461-L467)。
```python
    def get_request(self):
        """Get the request and client address from the socket.

        May be overridden.

        """
        return self.socket.accept()
```

此时 `self.socket` 仍是服务器的监听 socket。调用 `accept()` 后，返回值的第一个成员是新建的已连接 socket，第二个成员是客户端地址；赋值语句把它们分别命名为 `request` 与 `client_address`。socket 文档也明确区分 `accept()` 的连接结果与原监听 socket。接下来的 `finish_request` 把新连接传给 handler，而不是把监听 socket 交过去。

### 构造处理器时怎样把 socket 变成 `rfile` 和 `wfile`

基类构造器把已接受 socket、客户端地址和共享服务器对象分别存进处理器实例的 `request`、`client_address` 和 `server`，然后按顺序调用 `setup()`、`handle()`，并在 `finally` 中调用 `finish()`。`StreamRequestHandler.setup()` 将 `request` 赋给连接，并用它建立二进制 `rfile` 与 `wfile`。由此 `BaseHTTPRequestHandler.handle()` 能从同一个连接读请求、向它写响应；监听 socket 仍属于共享服务器对象。原始实现分别见 [`BaseRequestHandler.__init__` 原行 649–657](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L649-L657) 和 [`StreamRequestHandler.setup/finish` 原行 698–717](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L698-L717)。

这里有两种寿命不同的对象。服务器实例和 `RequestHandler.Cases` 列表跨连接存在；处理器实例携带一条已接受连接的 `self.path`、`self.full_path`、`rfile`、`wfile`。case 列表中的对象则不保留某个 handler，只在方法调用时接受当前 handler 参数。若把每个客户端的路径写进共享 case 实例，多条连接就会争用同一份可变状态；当前实现把连接状态留在 handler 上，规则对象只负责判断和委托。

#### 实例建立、读写流和清理：标准库原文

`BaseRequestHandler` 的初始化方法把生命周期写成直接的调用顺序。源码定位：CPython 2.7.18 `Lib/SocketServer.py`，`BaseRequestHandler.__init__` 原行 649–657；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L649-L657)。
```python
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()
```

构造调用收到的三个实参分别保存在新对象的三个字段中。`self.setup()` 先运行，给子类建立处理所需资源；`try` 包住 `handle()`，所以处理正常返回或抛出异常时都会执行 `finish()`。注意 `setup()` 在 `try` 外：若初始化读写流本身失败，这个 `finally` 尚未进入。项目继承的流处理器覆写 `setup()` 和 `finish()`，而 HTTP handler 再覆写 `handle()`。

流处理器实际把已接受 socket 包装为文件式对象。源码定位：`StreamRequestHandler.setup` 原行 698–706、`finish` 原行 708–717；[固定版本原文一](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L698-L706)、[固定版本原文二](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L708-L717)。
```python
    def setup(self):
        self.connection = self.request
        if self.timeout is not None:  # 教学注释：本例继承的默认值为None，因此跳过。
            self.connection.settimeout(self.timeout)
        if self.disable_nagle_algorithm:  # 教学注释：本例默认False，不设置TCP_NODELAY。
            self.connection.setsockopt(socket.IPPROTO_TCP,
                                       socket.TCP_NODELAY, True)
        self.rfile = self.connection.makefile('rb', self.rbufsize)  # 教学注释：读取缓冲大小来自类属性。
        self.wfile = self.connection.makefile('wb', self.wbufsize)  # 教学注释：输出缓冲大小也来自类属性。

    def finish(self):
        if not self.wfile.closed:
            try:
                self.wfile.flush()
            except socket.error:
                # A final socket error may have occurred here, such as
                # the local error ECONNABORTED.
                pass
        self.wfile.close()
        self.rfile.close()
```

#### 逐行读：连接字段、可选参数和流缓冲

原行 699 让 `connection` 指向 handler 保存的已接受 socket；没有新建第二条连接。`timeout` 的类属性默认是 `None`，所以第一个 `if` 跳过；若配置了非空值，`settimeout` 才会设置读写超时。`disable_nagle_algorithm` 默认是 `False`，第二个 `if` 也跳过。若改成真，`setsockopt(IPPROTO_TCP, TCP_NODELAY, True)` 会关闭 TCP Nagle 合并小段数据的算法；这可能降低某些小写入的等待，也可能增加小数据包，标准库注释提醒只在 `wbufsize != 0` 的配置下使用。当前例子两个条件都不成立。

默认类属性 `rbufsize=-1` 和 `wbufsize=0` 是 `makefile` 的第二个实参。`-1` 表示输入端采用默认缓冲，避免逐字节读取大型输入的低效；`0` 表示输出端不增加 Python 文件层缓冲，写出后可以及时继续读或结束响应。原行 705 的 `'rb'` 创建二进制输入文件对象给请求解析器；原行 706 的 `'wb'` 创建二进制输出文件对象给项目 `send_content`。两者都由 socket 的 `makefile` 建立，是连接流，不是磁盘文件。

#### 逐行读：finish 在什么范围内清理

`finish()` 若发现 `wfile.closed` 为假，就先尝试 `flush()`；原注释举出本地 `ECONNABORTED` 作为最后刷新可能遇到的 socket 错误。这里只有刷新步骤的 `socket.error` 被捕获并忽略。随后代码依次调用 `wfile.close()` 和 `rfile.close()`；如果这些关闭步骤本身抛出别的异常，源码没有额外捕获，所以不能把它说成无条件保证清理成功。即便清理调用都正常完成，也只说明程序关闭了流对象，不证明客户端已收到全部响应字节。

对当前请求而言，构造器的 `self.handle()` 进入 `BaseHTTPRequestHandler.handle()`，后者调用一次 `handle_one_request()`，并在 `close_connection` 为假时继续读同一连接的下一条请求。默认 HTTP/1.0 使本例通常走一次请求后关闭；若切换协议设置和连接条件，单个 handler 可能处理多条请求。`finish()` 是整个连接处理后的清理，不是 `do_GET` 返回后立刻执行；若 `setup()` 在 `BaseRequestHandler.__init__` 的 `try` 之前失败，则其对应的 `finish()` 也尚未进入。

Python 2.7.18 的官方 [`socketserver` 文档](https://github.com/python/cpython/blob/v2.7.18/Doc/library/socketserver.rst)说明 `BaseRequestHandler` 由 `setup`、`handle`、`finish` 组成；`StreamRequestHandler` 提供可读写的 `rfile` 与 `wfile`。[`socket` 文档](https://github.com/python/cpython/blob/v2.7.18/Doc/library/socket.rst)说明 `accept()` 返回新连接对象和地址，`makefile()` 返回与 socket 关联的类文件对象。这些定义对应本段的三个实参和两个流，不是另一个磁盘文件层。

### 请求行为什么最终调用覆写的 `do_GET`

`BaseHTTPRequestHandler.handle_one_request()` 从 `rfile` 读取一行，再调用 `parse_request()`。对 `GET /plain.html HTTP/1.1`，解析结果分别是 `self.command = 'GET'`、`self.path = '/plain.html'`、`self.request_version = 'HTTP/1.1'`。这一步只拆 HTTP 请求字段，不查磁盘。之后基类计算字符串 `mname = 'do_' + self.command`，得到 `'do_GET'`；先检查实例是否有该方法，再用 `getattr(self, mname)` 取出绑定方法并调用 `method()`。绑定使当前 handler 自动作为 `do_GET` 的 `self`，所以项目不需要自己再写一条调用语句。准确的解析与分派在 [`parse_request` 原行 232–299](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L232-L299) 和 [`handle_one_request` 原行 301–334](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L301-L334)。

解析代码先取得原请求行，再去掉末尾的 CR 和 LF，最后按空白拆成字段。源码定位：CPython 2.7.18 `Lib/BaseHTTPServer.py`，`parse_request` 原行 246–249；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L246-L249)。
```python
        requestline = self.raw_requestline
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()  # 教学注释：按空白拆成请求方法、目标和版本。
```

这里假定浏览器送来的请求行是 `GET /plain.html HTTP/1.1\r\n`。`rstrip('\r\n')` 只移除行尾回车/换行字符；`split()` 按空白切成 `['GET', '/plain.html', 'HTTP/1.1']`。本代码块只展示原行 246–249；后面的原行 250–287 没有贴出，其中还会检查字段数量、HTTP版本写法与数字、旧式两字段请求和空/畸形请求，并在不合法时尝试 400 或 505 后返回失败。它们是 `parse_request` 的实际控制逻辑，不能把这四行误当成完整解析器。行号链接与展示范围一致，见 [原行246–249](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L246-L249)。

字段解析完成后，原行 288–299 把局部变量转成当前 handler 的字段并读完头部。源码定位：同一 `parse_request` 原行 288–299；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L288-L299)。
```python
        self.command, self.path, self.request_version = command, path, version  # 教学注释：将三个局部变量解包存入当前handler。

        # Examine the headers and look for a Connection directive
        self.headers = self.MessageClass(self.rfile, 0)  # 教学注释：解析类从输入流读取请求头。

        conntype = self.headers.get('Connection', "")  # 教学注释：没有Connection头时取空字符串。
        if conntype.lower() == 'close':  # 教学注释：大小写不影响close比较。
            self.close_connection = 1
        elif (conntype.lower() == 'keep-alive' and
              self.protocol_version >= "HTTP/1.1"):  # 教学注释：两个条件都要成立。
            self.close_connection = 0
        return True  # 教学注释：调用者可继续分派请求方法。
```

#### 逐行读：局部值、头部解析和连接标志

原行 288 的多目标赋值把右侧三个局部变量依序放入 handler 的三个属性；代入本例就是 `command='GET'`、`path='/plain.html'`、`version='HTTP/1.1'`。逗号位置一一对应，不会按属性名自动查找。原行 290 的注释指出接下来关注 `Connection` 头。原行 291 通过类属性 `MessageClass` 创建解析对象，以 `self.rfile` 为输入，第二实参 `0` 告诉消息解析器按不可回退的流读取；解析出的头字段保存在这个 handler 的 `self.headers`。

原行 293 的 `.get('Connection', "")` 从头集合取值，缺失时用空字符串。`lower()` 只规范化比较用的副本，所以 `Close`、`CLOSE` 等写法都能命中小写 `close`。第一个 `if` 命中时把整数 `1` 写入 `close_connection`，表示不继续读同一连接；`elif` 只有前一个分支不成立才检查 `keep-alive`，括号中的 `and` 要求头值匹配且服务器响应 `protocol_version` 至少为 `HTTP/1.1`，两者成立才把标志置 `0`。没有这两种条件时，先前默认值保持不变。原行 299 的 `return True` 把“请求解析成功”的布尔值交给 `handle_one_request`，后者才会构造 `do_GET` 名称。项目读取 `self.path` 并组磁盘路径是在之后，因此请求解析和文件查找是两步。

`handle_one_request` 用这个已解析的 `self.command` 选择实例方法。源码定位：同一文件 `BaseHTTPRequestHandler.handle_one_request` 原行 317–328；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L317-L328)。下面只在难懂行尾加了明确的教学注释；原注释仍保留。
```python
            if not self.raw_requestline:  # 教学注释：空输入行表示连接已没有下一条请求。
                self.close_connection = 1
                return
            if not self.parse_request():  # 教学注释：失败时解析器已尝试发送错误响应。
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command  # 教学注释：'GET' 与前缀拼成属性名 'do_GET'。
            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)  # 教学注释：%r用repr形式显示方法名。
                return
            method = getattr(self, mname)  # 教学注释：从当前实例取绑定方法。
            method()  # 教学注释：绑定方法调用时把当前 handler 作为 self。
```

#### 原行 317–328：从空行到绑定方法调用

第一条 `if not self.raw_requestline` 检查刚读到的请求行是否为空；空输入就把 `close_connection` 设为 1 并返回，不会进入项目方法。接着 `parse_request()` 返回假时，解析器已经尝试发错误响应，当前方法直接返回。对本例，解析器先把命令存成 `self.command='GET'`，原行 323 的字符串加法得到 `mname='do_GET'`。

`hasattr(self, mname)` 查询当前实例及其类继承链上是否有这个属性。没有就调用 `send_error(501, ...)` 后返回；这里旧式 `%` 格式里的 `%r` 用 `repr` 表示命令值，`self.command` 是 `'POST'` 等文字，因此错误消息会引用它。原行 327 的 `getattr(self, mname)` 按字符串名字取出方法；因为访问对象是 handler 实例，得到的是已绑定方法。原行 328 的 `method()` 没显式传入 handler，但调用时 Python 已把该实例绑定为方法的首个 `self` 参数，故实际效果是 `handler.do_GET()`。

因此给定 `GET` 时动态查找继承到的项目覆写方法，`do_GET` 才执行；若是 `POST` 而类中没有 `do_POST`，走基类 501 分支，不会先查磁盘，也不会到项目的 404 case。`return` 只结束本次 `handle_one_request`，后续清理仍由外围 handler 生命周期完成。

CPython 2.7.18 的官方 [`BaseHTTPServer` 文档](https://github.com/python/cpython/blob/v2.7.18/Doc/library/basehttpserver.rst)把这条规则写成：handler 解析请求和头部，再按请求方法构造 `do_*` 方法名，相关信息保存在 handler 实例变量中；实现具体方法即可，通常不需要覆写 `__init__` 或通用分派。文档里的 `SPAM → do_SPAM()` 例子与本课 `GET → do_GET()` 使用同一约定。上面贴出的实现补足文档没有逐句展示的 `hasattr`、`getattr` 和绑定调用。

如果方法名不是 `GET`，例如 `POST`，基类会找 `do_POST`。本项目没有实现它，因此基类调用自己的 `send_error(501, ...)` 并结束该处理；它不会进入项目 `do_GET` 的 `try`，也不会先检查文件是否存在。标准库的 501 分支见 [`handle_one_request` 原行 323–328](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L323-L328)，其错误响应实现见 [`send_error` 原行 344–384](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L344-L384)。这与项目将 `GET /missing.html` 转成 404 是两条不同的错误链。

### 请求版本和响应版本由不同字段控制

解析阶段把客户端版本存到 `self.request_version`；响应状态行使用类属性 `protocol_version`。CPython 2.7.18 将后者默认设为 `HTTP/1.0`，项目子类没有覆盖它。因此浏览器发 `HTTP/1.1` 请求，项目仍正常用 `HTTP/1.0` 状态行回应。基类 `send_response()` 从 `protocol_version` 格式化状态行，并在随后加上标准 `Server`、`Date` 头；默认值见 [`protocol_version` 原行 511–518](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L511-L518)，写出规则见 [`send_response` 原行 389–408](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L389-L408)。

基类中的默认值是类属性，定义在 `BaseHTTPRequestHandler` 上。源码定位：CPython 2.7.18 `Lib/BaseHTTPServer.py` 原行 511–518；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L511-L518)。
```python
    # Essentially static class variables

    # The version of the HTTP protocol we support.
    # Set this to HTTP/1.1 to enable automatic keepalive
    protocol_version = "HTTP/1.0"

    # The Message-like class used to parse headers
    MessageClass = mimetools.Message
```

`protocol_version` 属于处理器类，项目子类没有重设它，所以当前实例从继承关系读取到 `HTTP/1.0`。客户端的 `request_version` 则是前面解析请求行写入的实例字段，示例值是 `HTTP/1.1`。这两个值服务于不同方向：前者写服务器响应和决定标准库能否保持 HTTP/1.1 连接，后者描述客户端请求并用于兼容旧式请求处理。`MessageClass` 是读头部时使用的解析类，不等于项目的 `Cases` 规则列表。

官方 [`BaseHTTPServer` 文档的 `protocol_version` 说明](https://github.com/python/cpython/blob/v2.7.18/Doc/library/basehttpserver.rst)特别指出：默认 `HTTP/1.0` 为向后兼容；若改为 `HTTP/1.1` 以允许持久连接，服务端每个响应都必须含准确的 `Content-Length`。这解释了为何版本字段不只是状态行装饰，也会改变连接何时继续读下一条请求。

处理器也不是普遍意义上的“一条 HTTP 请求一个实例”。标准库按已接受的 TCP 连接构造 handler；之后 `handle()` 会在 `close_connection` 为假时继续处理同一连接上的下一条请求。对 HTTP/1.1 输入，`parse_request()` 只有在服务器 `protocol_version` 也至少是 HTTP/1.1 时才允许 keep-alive（在同一条 TCP 连接上继续处理后续请求）；本例默认 HTTP/1.0，所以这个例子的一条连接通常只处理一次请求并关闭。若改变服务器协议设置，生命周期就可能变成一个连接上的多个请求。可核对 [`parse_request` 的连接判断](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L270-L299) 和 [`handle` 循环](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L336-L343)。

MIME 是 Multipurpose Internet Mail Extensions（多用途互联网邮件扩展）；这里的旧式 API 用它称呼头部，HTTP 的 `Content-Type` 值则标出媒体类型：`text/html` 表示按 HTML 解释，`text/plain` 表示纯文本。当前项目发送 `text/html`。

### 响应头和正文如何按顺序写出

项目 `send_content` 先让基类写状态行及标准头，随后项目依次写 `Content-type` 与 `Content-Length`，调用 `end_headers()` 写结束空行，最后对 `wfile` 写正文。基类的头部方法原文位于 [`send_response`、`send_header`、`end_headers` 原行 389–423](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L389-L423)。在标准库 2.7.18 的 `StreamRequestHandler` 中，`wbufsize = 0`，写接口不做 Python 层缓冲（设置和创建位置见 [原行 681–706](https://github.com/python/cpython/blob/v2.7.18/Lib/SocketServer.py#L681-L706)）；具体每次底层写入仍可能因连接错误而失败。TCP 层的写入成功和浏览器端完整接收仍是不同事实。

#### 标准库按什么顺序把响应写到连接

源码定位：CPython 2.7.18 `Lib/BaseHTTPServer.py`，`send_response`、`send_header`、`end_headers` 原行 389–423；[固定版本原文](https://github.com/python/cpython/blob/v2.7.18/Lib/BaseHTTPServer.py#L389-L423)。
```python
    def send_response(self, code, message=None):
        """Send the response header and log the response code.

        Also send two standard headers with the server software
        version and the current date.

        """
        self.log_request(code)  # 教学注释：记录状态码；日志不是响应正文。
        if message is None:  # 教学注释：调用者没给状态短语时才查映射表。
            if code in self.responses:  # 教学注释：只对已知状态码取标准短语。
                message = self.responses[code][0]  # 教学注释：表项第0位是短语。
            else:
                message = ''  # 教学注释：未知状态码没有默认短语。
        if self.request_version != 'HTTP/0.9':  # 教学注释：旧式请求不写状态行。
            self.wfile.write("%s %d %s\r\n" %
                             (self.protocol_version, code, message))  # 教学注释：旧式%格式依次填协议、整数状态、短语。
            # print (self.protocol_version, code, message)
        self.send_header('Server', self.version_string())  # 教学注释：追加服务器标识头。
        self.send_header('Date', self.date_time_string())  # 教学注释：追加生成时的日期头。

    def send_header(self, keyword, value):
        """Send a MIME header."""
        if self.request_version != 'HTTP/0.9':  # 教学注释：HTTP/0.9没有头部格式。
            self.wfile.write("%s: %s\r\n" % (keyword, value))

        if keyword.lower() == 'connection':  # 教学注释：头名比较不区分大小写。
            if value.lower() == 'close':  # 教学注释：请求/响应要求关闭时设置标志。
                self.close_connection = 1
            elif value.lower() == 'keep-alive':  # 教学注释：保持连接时清除关闭标志。
                self.close_connection = 0

    def end_headers(self):
        """Send the blank line ending the MIME headers."""
        if self.request_version != 'HTTP/0.9':  # 教学注释：写头部结束所需的空行。
            self.wfile.write("\r\n")
```

#### 原行 389–407：短语查表和状态行格式

`send_response(code, message=None)` 收到项目传来的整数状态码，短语默认 `None`。原行 396 调用 `log_request(code)` 记录状态；日志不写进响应正文。原行 397 只在 `message is None` 时查短语，调用者若显式给短语便沿用它。原行 398 以 `code in self.responses` 检查状态表是否有这个整数键；例如 200 的第一项是 `OK`，404 的第一项是 `Not Found`。原行 399 的 `[code][0]` 先选状态对应的元组，再取第 0 项短语；如果状态不在表中，原行 401 改用空字符串，避免访问不存在的键。

原行 402 跳过 HTTP/0.9 的状态行；其他请求会走原行 403 的 `%` 格式表达式。`%s %d %s\r\n` 依次取 `self.protocol_version`、整数 `code`、短语 `message`，并以回车换行结束状态行。`# print (...)` 是原作者留着的注释调试行，不执行。原行 406–407 调用同一个头部方法写 `Server` 与 `Date`。项目的 `send_content` 调用 `send_response(200)` 或 `send_response(404)`，没传第二个实参，所以短语由表决定。

#### 原行 409–423：头部值、连接标志和结束空行

`send_header(keyword, value)` 收到头名称和值。原行 412 用 `%s: %s\r\n` 依次把名称和值写成头行；HTTP/0.9 时跳过这次头部写入。之后即使不写头，原行 414 仍会检查头名：`keyword.lower()` 让比较不受大小写影响；只有名称是 `connection`，才会将 `value.lower()` 与 `close` 或 `keep-alive` 比较，并分别把 `close_connection` 设为 1 或 0。项目这里发的是 `Content-type` 和 `Content-Length`，所以不改连接标志。

原行 420 定义 `end_headers()`，原行 421 是它的文档字符串，原行 422 检查请求版本，原行 423 才写一个 CRLF。此前每个头行自身已经有 CRLF；这次额外的空行才表示头部结束，后面的 `wfile.write(content)` 才能开始正文。标准库 `.rst` 对三个 API 的说明给出相同的外部顺序；CPython 2.7.18 源码表明这些调用直接写到 `wfile`，不是先放进 Python 3 的 `headers_buffer`。

CPython 2.7.18 的这些方法直接 `write` 到 `wfile`；不存在 Python 3 `http.server` 后来使用的 `headers_buffer` 暂存列表。当前 `StreamRequestHandler` 又设置 `wbufsize = 0`，所以每次程序写入会直达 socket 写接口；这仍不等同于浏览器已经收齐。项目逐行调用响应方法时，若中途 `IOError`，之前已写出的状态/头部/正文前缀都无法撤回，失败处理也不能将它们变成一条保证完整的 404。

官方 [`BaseHTTPServer` 文档的响应方法说明](https://github.com/python/cpython/blob/v2.7.18/Doc/library/basehttpserver.rst)分别描述 `send_response` 写响应行和 Server/Date 头、`send_header` 写一项头、`end_headers` 写结束空行；它们的次序正好对应源码中的直接写入。文档定义这些 API 的可见行为，Python 2.7.18 实现则说明了本版本直接写入 `wfile` 的具体机制。

成功时磁盘返回 `plain.html` 字节，`send_content` 默认状态为 200，长度按 Python 2 字节串 `len(content)` 计算。缺失路径和普通目录由项目 case 抛出 `ServerException`，然后 `handle_error` 显式传 404；不支持的 POST 则是基类 501。状态是应用写入响应的结果，不是磁盘异常自动转化出来的值。网络写失败若发生在状态或部分头部之后，源码仍会尝试错误出口，但已经交给连接的字节无法被撤回；真实结果只能描述为可能部分输出、再次写失败或连接中断。


## 7. 同一组数据的正常与失败回放

### 正常输入：`GET /plain.html`

沿用第四章的假设工作目录和同一 URL。标准库先得到 `command='GET'`、`path='/plain.html'`；`command` 用来让基类分派到 `do_GET`，而项目只把当前工作目录与 `self.path` 拼成 `full_path='/work/500lines/web-server/code/03-handlers/plain.html'`。`case_no_file.test` 检查该路径存在，结果为假；`case_existing_file.test` 检查它是文件，结果为真；`case_existing_file.act` 调 `handle_file`。`open(..., 'rb')` 返回的 reader 读取整份 HTML，随后关闭文件，`content` 包含其字节。

固定提交的原始 `plain.html` 是 LF 换行文本，九个换行符都在文件字节中；按原始字节逐个计算共 116 字节，所以对这个原始文件，`Content-Length` 静态推演值为 `116`。这是对源码数据的计算，不是请求运行记录；若 checkout 把九个 LF 都改为 CRLF，文件会多 9 字节而成为 125 字节。`handle_file` 以 `rb` 读取实际文件，再用实际 `len(content)` 生成长度，因此头部跟随读入字节数，不是固定常量。[原始文件九行](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/plain.html#L1-L9)。

`handle_file` 没有给 `send_content` 传第二个参数，所以状态仍为 200。响应头说明 HTML 类型与正文长度；头部结束空行之后才写出文件内容。浏览器把正文解析为文档，用户看到 `Plain Page` 标题和 `Nothin' but HTML.` 段落。此链条是按代码逐步静态推演的预期结果，不是本机浏览器运行记录。

### 失败输入一：文件不存在

只把路径改为 `/missing.html`。`full_path` 随之成为当前工作目录下的 `missing.html`。第一条 `case_no_file.test` 返回真，`case_no_file.act` 抛出 `ServerException("'/missing.html' not found")`。异常让循环中的 `break` 和后续 case 都不执行，控制流直接进入 `do_GET` 的 `except`。`handle_error` 用同一个 `self.path` 和异常文字填入错误模板，并调用 `send_content(content, 404)`，于是响应状态是 404，正文包含标题 `Error accessing /missing.html` 以及错误文字。项目没有创建、修改或删除任何磁盘文件。

### 失败输入二：路径指向目录

若请求 `/subdir` 且当前目录确实有 `subdir` 目录，第一条规则因 `exists=True` 而返回假；第二条规则因 `isfile=False` 也返回假。第三条规则必定为真，它抛出 `Unknown object '/subdir'`，共同错误出口回 404。这个版本没有目录索引页或目录清单；不能因为 `subdir` 存在就推断它会返回目录内容。

### 失败输入三：检查和打开之间文件消失

假设另一个进程在 `case_existing_file.test` 确认文件存在之后、`open(full_path, 'rb')` 之前删除文件。前两次判断已经选中普通文件分支，但 `open` 此时抛 `IOError`。`handle_file` 捕获它并以 `cannot be read` 的消息进入同一个 404 错误页路径。若错误页的响应写出正常完成，控制会从 `handle_error` 正常回到 `handle_file` 的 `except` 末尾；两者都没有显式返回值，所以依次把 `None` 交回 `case_existing_file.act` 和 `do_GET`，原行 75 的 `break` 仍会执行。相反，缺失路径的 `case_no_file.act` 抛出的 `ServerException` 没有在动作内部捕获，直接跳到 `do_GET` 的 `except`，因此会跳过 `break`。这说明“规则匹配后”并不等于“循环立即退出”：动作必须正常结束才走到 break。此推演不是实测；它说明先检查存在不能保证稍后的打开一定成功。

### 失败输入四：响应输出中途发生 IOError

另一个不同的假设是文件已经完整读入，但 `send_content` 在写响应时抛出 `IOError`。这次异常也落进 `handle_file` 的同一个 `except`，所以代码会把网络输出故障包装成“文件不可读”，再尝试生成 404。若失败发生在状态行或头部写出之后，连接上可能已有 `200` 或部分响应字节；继续写 404 不会自动清除它们，第二次写也可能再次失败。因此此路径的实际结果不能描述成“浏览器一定收到 404”；这只是从 `try` 的范围和逐步写响应的顺序得出的边界分析，没有模拟网络故障。

### 容易看错的两种结果

`/plain.html?rev=2` 中的问号和 `rev=2` 是常见查询文字，但标准库把请求目标整体放进 `self.path`；项目既不切掉查询部分也不解析它，而是直接拼接路径。若工作目录下没有名为 `plain.html?rev=2` 的字面文件，文件检查就会失败。另一个容易混淆的点是 `send_content` 的默认状态：只有成功文件路径用默认的 200；错误出口显式传 404。若把默认值改为 404，正常文件响应也会变成错误状态。

### 一次响应结束后，处理器和连接怎样收尾

在正常 `/plain.html` 路径里，项目 `do_GET` 写完正文后返回；继承的 `BaseHTTPRequestHandler.handle_one_request()` 随之返回给 `handle()`。默认响应协议是 HTTP/1.0，连接关闭标志通常保持为真，因此 `handle()` 不再循环读下一条请求。随后 `BaseRequestHandler.__init__` 的 `finally` 调 `finish()`：流处理器尝试刷新仍打开的 `wfile`，再关闭读写流。处理器构造调用返回后，`BaseServer.process_request()` 调 `shutdown_request(request)`；TCPServer 结束已接受连接并关闭 socket。监听 socket仍归服务器持有，供下一轮 `serve_forever` 接受新连接。

缺失文件时，项目异常先被 `do_GET` 捕获并尝试写 404；若写出成功，接着走同一条 `handle_one_request`、`handle`、`finish`、`shutdown_request` 收尾链。文件读取失败也可能在 `handle_file` 内部转换为错误页后正常回到规则循环，再执行 `break`，然后走正常清理。若状态、头部或正文写入抛错，错误页的第二次写入也可能失败，异常再交给服务器级错误钩子；清理代码仍尝试刷新/关闭流和连接，但它不能撤回已写字节，也不能证明浏览器收到了完整页面。本文只把 `200` 或 `404` 页面描述为整条相应写出成功时的可见结果。

## 8. 设计取舍与使用/扩展方法

### 在历史环境里怎样按实际入口查看页面

这份代码从进程当前工作目录拼出目标路径；因此开始前要把终端切到包含 `plain.html` 的实际目录，即检出仓库里的 `web-server/code/03-handlers/`。以下命令只描述操作，不是本课执行记录；`<500lines-checkout>` 是占位符，须替换成自己检出的仓库完整路径。只有已经有隔离的 Python 2.7 环境时才用对应解释器启动，不需要为只读学习安装旧运行时：

```powershell
Set-Location '<500lines-checkout>\web-server\code\03-handlers'
python2.7 .\server.py
```

第一条命令改变工作目录；第二条直接执行脚本，没有目录参数。启动时主入口绑定源码常量端口 8080，`os.getcwd()` 因而应得到这个 `03-handlers` 目录。进程不会打印项目自定义的“启动成功”文字，因为源码没有该打印语句。若系统找不到 `python2.7`，表示当前环境没有这个命令；若绑定时端口已被占用，服务器构造会报错并无法监听；若工作目录不对，请求目标就会映射到错误位置。

进程已启动时，在浏览器打开 `http://127.0.0.1:8080/plain.html`。按静态代码推演，若该目录下确有原始文件，成功响应状态应为 200，页面主体显示 `Plain Page` 和 `Nothin' but HTML.`，标签页标题为 `Plain Page`。若打开 `http://127.0.0.1:8080/missing.html`，项目应尝试返回 404 和错误 HTML。上面是阅读代码可以推导的预期信号，不是浏览器实测。关闭等待中的历史进程可在其终端按 Ctrl+C。

源代码把主机值写成 `''`；对该版 IPv4 socket，它代表 `INADDR_ANY`，会在本机所有可用 IPv4 接口监听。浏览器用回环地址连接并不会把服务器本身限制为回环监听，因此不要把原样示例放进共享网络。若只打算在本机隔离演示，可以将入口地址改成 `('127.0.0.1', 8080)`；这是对固定示例的源代码修改，不是它当前的默认行为。

### 同一提交的真实扩展：请求目录时读取 `index.html`

固定提交的同一目录还包含独立变体 [`server-index-page.py`](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server-index-page.py)。主课的 `server.py` 没有目录首页规则；以下是变体新增的完整 case 类，原始连续行 33–44。这里只摘新规则和下方注册片段；HTTP 解析、请求循环、公共文件读取和响应发送已在主课中展开，不重复粘贴。

假设当前工作目录仍是 `/work/500lines/web-server/code/03-handlers`，浏览器请求 `/guide`。项目先把请求目标拼到 `handler.full_path`，得到 `/work/500lines/web-server/code/03-handlers/guide`。这个 case 要判断它是否是目录，以及该目录下的首页是否真是一个文件：

```python
class case_directory_index_file(object):  # 教学注释：这是独立变体新增的目录首页规则。
    '''Serve index.html page for a directory.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')  # 教学注释：返回 guide/index.html 的完整路径。

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))  # 教学注释：目录与首页文件都成立才匹配。

    def act(self, handler):
        handler.handle_file(self.index_path(handler))  # 教学注释：复用处理器已有的读文件和发送流程。
```

原行 33–34 定义 `case_directory_index_file` 并说明职责。原行 36–37 的 `index_path(self, handler)` 是 case 实例的方法：调用时 case 自动绑定为 `self`，当前 `RequestHandler` 则由调用点作为 `handler` 传入。`os.path.join('/work/500lines/web-server/code/03-handlers/guide', 'index.html')` 组合成 `/work/500lines/web-server/code/03-handlers/guide/index.html`；它只算路径字符串，不打开文件，也不发送响应。完整原段见 [变体原行 33–44](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server-index-page.py#L33-L44)。

原行 39–41 的 `test` 先用 `os.path.isdir(handler.full_path)` 检查请求目标是不是目录。`and` 在左侧为假时会短路，不会计算右侧；只有目录存在，才调用 `self.index_path(handler)` 并用 `os.path.isfile(...)` 检查首页路径是否是普通文件。这里的 `self` 仍是共享 case 对象，`handler` 才带着本次连接的 `full_path`。所以“目录存在”单独不足以匹配，首页文件也必须存在。

源码第 40 行末尾的反斜线是显式续行符：它把第 40、41 两个物理行接成同一条 `return` 表达式，不是字符串里的反斜线。`os.path.isdir` 和 `os.path.isfile` 都返回布尔值；`and` 短路后得到的真假值就是 `test` 返回给 `if` 的条件。

原行 43–44 的 `act` 再次计算这个路径，并调用 `handler.handle_file(...)`。它把目录首页交给已有处理器读取和发送；`do_GET` 不消费 `act` 的返回值，真正的响应仍来自 `handle_file` 的副作用。若文件读取及响应写出正常结束，动作正常返回，循环才执行后续 `break`。

变体的完整 `Cases` 注册片段是原行 65–68：

```python
    Cases = [case_no_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]  # 教学注释：新规则放在普通文件之后、兜底规则之前。
```

这张有序表先处理不存在的路径，再把普通文件交给原来的文件 case，随后才尝试目录首页，最后由恒真的 `case_always_fail` 兜底；逐行见[变体原行 65–68](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server-index-page.py#L65-L68)。普通文件 `/plain.html` 仍由第二条规则读取，正常发送后 `break` 会阻止目录规则接手。若请求 `/guide` 且目录及其 `index.html` 都存在，前两条 `test` 返回假，目录规则依次得到 `isdir=True`、`isfile=True`，调用 `handle_file('/work/500lines/web-server/code/03-handlers/guide/index.html')`，沿用默认 200 响应。若目录存在但没有 `index.html`，`isdir=True`、`isfile=False`，目录规则不匹配，最终由兜底规则抛出 `ServerException` 并走项目 404 错误页。这里假设的目录和首页文件只用于静态推演，不是仓库实测内容。

若要对照运行这个同提交变体，工作目录仍须切到前一小节的 `web-server/code/03-handlers/`，只把脚本换成 `python2.7 .\server-index-page.py`；变体入口原行 121–124 仍设置空主机和端口 8080，见[启动代码](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server-index-page.py#L121-L124)。这是可选的历史环境操作说明，不是运行记录。

### 三个实现选择会怎样改变接线

#### 有序规则表，还是一个 `if/elif`

当前 `Cases` 把判断和动作分开放在多个对象里，`do_GET` 统一扫描并在动作正常返回后 `break`。新增行为时，要新增规则对象并把实例注册在正确位置；目录首页变体的原行 65–68 就是在普通文件与兜底之间插入目录规则。如果这个例子永远只有三种情况，直接在 `do_GET` 写 `if not exists / elif isfile / else` 也能表达顺序，少一些类和方法跳转；代价是再加行为就继续增长同一段分支，而且判断、委托位置都集中回 handler。选哪种取决于规则数和是否需要独立扩展；两种写法都必须让兜底最后运行，改动后还要沿 `do_GET` 的首个匹配与退出条件重走 `/plain.html`、`/missing.html`、`/subdir`。

#### 共享无状态规则，还是在处理器实例保存数据

本例在类定义时只创建一份 case 列表，并把当前 handler 显式传给每次 `test`、`act`；case 不把 `full_path` 赋给自己的字段。这样多个连接会复用规则对象，却各自读取自己的 handler 状态。若某条规则要缓存每连接信息，可把该值放在 handler 字段，或者在 handler 初始化阶段构建实例级规则表，而不要写进共享 case 的可变字段。若信息属于单个 HTTP 请求而非整个连接，需在每次 `do_GET` 开始时更新/清理它；启用 keep-alive 后同一个 handler 可能处理多条请求，单纯“每连接创建一次”仍可能留下上一请求值。改动点是 `RequestHandler.Cases` 的类/实例归属和 `do_GET` 的赋值/调用，而非静态 `case.test` 文本本身。

#### 一次读完整文件，还是分块发送

当前 `read()` 把整份文件放进 `content`，所以 `len(content)` 可直接写入 `Content-Length`，发送方法只需一次正文写调用；代码容易沿“磁盘字节到响应正文”推演，代价是内存随文件大小增长。分块读取可降低峰值内存，但必须决定长度如何取得并应对检查后文件大小变化，或改用合适的响应结束策略；还要把 `handle_file` 的单个 `content` 实参改成循环写块的流程，并审视 `send_content` 的头部和 handler 的连接复用。不能只把 `reader.read()` 换成循环，因为当前 `Content-Length` 消费的是完整正文长度，且发送中失败的处理边界也会改变。

### 修改响应类型或文件根目录时要改消费值的地方

MIME（Multipurpose Internet Mail Extensions，多用途互联网邮件扩展）定义内容类型标签；HTTP 把媒体类型写在 `Content-Type` 头中。当前 `send_content` 对所有正文都写 `Content-type: text/html`，所以浏览器按 HTML 解释。若扩展为 `.txt`，应按实际文件类型选择媒体类型，例如 `text/plain` 表示纯文本，并确保发送字节与长度头一致；当前代码没有这项区分。

若要让调用者指定文件根目录，也不能只给脚本增加一个参数：入口没有读取 `sys.argv`，而路径来自 `os.getcwd() + self.path`。要新增配置读取，还要定义请求目标如何变为文件系统路径，并保证映射后的实际文件仍位于允许的根目录。当前表达式不规范化 `..`，也不验证最终路径边界。假设根目录是 `/srv/site`，请求 `/../private.txt` 会拼成 `/srv/site/../private.txt`；文件系统解析 `..` 后可能到达 `/srv/private.txt`。若该目标存在且为普通文件，当前 case 会读取它。

错误页中的 `self.path` 和 `msg` 也经 `.format(...)` 原样写入 HTML，没有 HTML 转义；请求目标若含标签字符，浏览器可能把错误文字中的内容当成标记。真实服务需要按 HTML 上下文转义错误正文。这个边界来自原模板和格式调用，不能因浏览器正常显示普通 `/missing.html` 就推断任意输入都安全。

最后，`reader.read()` 会把整个文件放进内存，之后一次性写正文；请求由同步 `TCPServer` 顺序处理。这样代码容易展示“文件字节如何变成响应”，但大文件会增加内存占用，慢 I/O 会延迟后续连接。若将来改为分块读取或并发服务，必须重新设计正文长度/传输结束条件与连接处理，不能只把一行 `read()` 换掉就认为整条协议链保持相同。


## 9. 易混淆点与带答案复习

### 请求与响应版本分别由哪个字段决定

浏览器送来 `GET /plain.html HTTP/1.1` 时，解析器把 `HTTP/1.1` 存入当前 handler 的 `request_version`；响应状态行却从类属性 `protocol_version` 取值，CPython 2.7.18 的默认是 `HTTP/1.0`。所以本例可静态推导为 `HTTP/1.0 200 OK`，并不要求请求与响应版本文字相同。若误把 `request_version` 当作服务器设置修改，响应版本不会因此变化；若把服务器改成 HTTP/1.1，还必须保证响应长度和连接行为符合该设置。细节见[第六章版本字段小节](#请求版本和响应版本由不同字段控制)。

### Python异常怎样变成HTTP 404

对 `/missing.html`，第一条规则的 `test` 返回 `True`，但动作抛出的只是 Python `ServerException`；`do_GET` 的 `except` 才把异常对象交给项目 `handle_error`，由它显式调用 `send_content(content, 404)`。如果把“raise 自动等于 HTTP 404”当成规则，改掉统一错误处理后就会误判响应。对 `/plain.html` 的文件写出异常则可能已经有状态行或头部，因此不能把每个捕获到的 `IOError` 都推导为浏览器必定得到完整 404。见[第5.8节错误页与发送调用](#58-错误路径显式选-404发送方法负责共同格式)和[第七章失败回放](#失败输入四响应输出中途发生-ioerror)。

### 规则列表和处理器实例何时创建

`RequestHandler` 类体执行一次时，`Cases` 列表里的三个 `case_*()` 调用各自创建一个规则对象；不是每个请求都再建一张表。服务端 `accept()` 每得到一条连接，才用 handler 类构造连接处理器。默认 HTTP/1.0 下连接通常处理一条请求；若将服务器协议与连接条件改为 keep-alive，一个 handler 可能处理同一连接上的多条请求。把请求路径保存到共享 case 字段会让多个连接看到同一个可变槽位；当前规则显式接收 handler，路径留在各自实例上。见[类属性与实例状态](#共享类属性和请求实例属性怎样区别)。

### `case.test(self)`中的两个self分别是谁

外层 `do_GET` 的 `self` 是本次 handler，记作 `H`；若局部 `case` 是规则对象 `E`，调用 `case.test(self)` 进入方法后就是 `E.test(self=E, handler=H)`。点号左边对象自动绑定到方法的首参数，括号内的 `H` 仍按位置传给 `handler`。因此在规则里读取 `handler.full_path` 才会得到 `/work/500lines/web-server/code/03-handlers/plain.html`；如果误把规则里的 `self` 当成 handler，就会访问错误对象上的字段。完整值传递见[第3章对象绑定示例](#类实例方法参数怎样组成这条调用)。

### `exists`检查成功后`open`仍可能失败

假设 `isfile('/work/500lines/web-server/code/03-handlers/plain.html')` 返回 `True`，但另一进程随后删除了文件；`handle_file(full_path)` 仍可在 `open(full_path, 'rb')` 处抛出 `IOError`。检查只回答那一刻的状态，不锁定路径或替后续打开预约文件。若误认为判断成功就保证打开成功，`except IOError` 就会显得多余；实际代码要在读取处保留错误路径。读取错误发生在成功响应开始前，而网络发送错误可能发生在 200 状态或部分头部已经写出后，两者虽同为 `IOError`，可见结果不同。见[第5.3节规则动作和失败链](#53-存在且为普通文件时把路径交给处理器读取)。

### `Content-Length`数的是最终字节

本例 `open(..., 'rb')` 让 `content` 是字节串；`len(content)` 对原始 `plain.html` 得 `116`，因为这份 LF 文件含 116 个字节。若内容是 Python 2 的 `u'中'`，字符长度是 1；先 `encode('utf-8')` 得 `E4 B8 AD` 三个字节，头部就要按编码后的三字节计。误把 Unicode 字符个数写作长度，会让接收端按错误边界读取正文。详见[第3章字符、编码与长度示例](#文件字节怎样成为浏览器能解释的-html)。

### 命令行目录参数是否改变文件根目录

运行 `python2.7 server.py some-folder` 时，`some-folder` 只是进入 `sys.argv` 的文字；本文件虽然 `import sys`，但没有读取它。入口仍把 `('', 8080)` 作为地址传给服务器，路径仍由 `os.getcwd() + self.path` 形成。例如终端当前目录为 `/work/.../03-handlers` 且目标为 `/plain.html`，最终路径就是 `/work/.../03-handlers/plain.html`。误把脚本路径或命令行尾参当作文件根目录，会导致工作目录一变就找错文件。见[第5.9节入口实参](#59-主入口把处理器类交给监听服务器)。

### `GET`和`POST`为什么进入不同错误路径

对 `GET /missing.html`，标准库找到项目覆写的 `do_GET`，再由项目规则抛异常并明确选择 404。对 `POST /missing.html`，标准库会查找 `do_POST`；当前项目没有这个方法，于是标准库在文件规则之前发送 501。若以为所有方法都先查文件，便会错误预测为项目 404。方法名构造与绑定调用见[第六章动态分派小节](#请求行为什么最终调用覆写的-do_get)。

这些题目用实际值复走正文中的关键边界；答案是教学笔记，不是要求读者先作答的测验，也不代表读者已经掌握。


## 10. 本课收获、证据边界与下一课

本课走通的因果链是：启动脚本时创建共享 case 对象和监听服务器；浏览器把 `GET /plain.html` 写入 TCP 连接；Python 2.7 标准库解析请求行、给当前处理器设置 `command` 与 `path`，再按命名规则调用覆写的 `do_GET`；项目用当前工作目录拼出磁盘路径，按顺序试 `exists`、`isfile` 和兜底规则；文件 case 以二进制方式读取内容，再由 `send_content` 写出状态、头部和正文；浏览器按 `text/html` 解析正文。缺失文件会先转成 Python 异常，再由项目映射成 HTTP 404。

证据限于固定 AOSA 源码和 CPython 2.7.18 的标准库实现与文档，以及 HTTP 消息格式标准；工作目录、请求值和结果展示是明确标出的静态例子。没有在当前机器安装或运行 Python 2，没有启动网络服务、发请求、打开浏览器或观察响应。特别是当前 `server.py` 使用空主机地址、当前目录拼路径、完整读入文件并把错误文字原样写入 HTML；本文解释这些实际边界，不把示例描述为安全或生产可用的服务。

### 读完后可以实际做的读码练习

在不启动服务的情况下，重新打开固定提交 `server.py` 原行 69，把工作目录设为假设值 `/srv/site`，分别把 `self.path` 代入 `/plain.html` 和 `/../private.txt`。写下当前 `+` 拼接的原始结果，再逐步指出是哪一处把字符串交给 `os.path.isfile`、哪一处交给 `open`。接着在纸上或自己的临时副本里提出一条规则：只允许规范化后的目标仍位于 `/srv/site` 之下，并说明越界时如何沿现有异常和 `handle_error` 出口反馈。用 `/plain.html`、`/missing.html`、`/../private.txt` 三个输入逐一检查你的规则顺序和调用者；这是一项具体的阅读/设计练习，本文不替读者填写答案，也不要求提交作业。

### 已展开、静态推演和未实测的边界

AOSA 项目语句及原注释、固定提交中的 `plain.html` 字节数、CPython 2.7.18 的类/方法实现，是本文引用的源码事实；HTTP 消息边界来自 RFC 9112 的一般说明。`/work/500lines/...`、浏览器发出的请求和 `/guide/index.html` 是标明的教学输入，输出说明是按这些输入逐步推导的结果，不是运行记录。没有安装 Python 2.7、运行服务器、发送请求、打开浏览器，也没有实测 bind 冲突或网络写中断。本文只说明本版本实际展示的处理路径，不据此宣称它完整符合 HTTP/1.1，也没有展开路径规范化、权限模型或生产部署方案。

### 下一课从哪个调用点继续

下一课目标是：保留 `/plain.html` 的读取行为，同时让 `/../private.txt` 无法越过配置的静态文件根目录。可以从原行 69 的 `full_path` 构造开始，继续追到 `case.test` 的文件判断、`handle_file` 的 `open` 和错误页调用点，比较 URL 解码、路径规范化、根目录包含检查及失败响应该放在哪里。预期交付是一份带有真实接线位置和三种输入推演的安全路径设计；后续依据读者能否独立解释、预测、实验或重建来评估掌握；读过或交付这份笔记本身不等于掌握，也不构成阅读门禁。

## 历史局部读码参照：从 Markdown 标题算出本地链接锚点

> 以下原稿保留了正确的局部 Python 语法、值变化和错误传播讲解。它示范的是一个标题转换 helper 的精读范围，不再作为完整功能课的主例或篇幅、架构深度验收基准。
### 1. 业务场景与本课目标

维护者改完文档后，发布检查要发现失效的本地链接，避免文档指向一个并不存在的文件或标题。这里的发布检查是仓库在交付前运行的一组自动检查；它读取仓库文件并给出通过或失败结果。Markdown 是用普通文字和少量标记写文档的格式；下面的 `## Setup` 用两个井号表示二级标题。

本课只跟一条链接：源文档在 `ROOT/docs/start.md`，目标文档在同一目录的 `ROOT/docs/guide.md`，两份文件都已在本次检查读取的文件集合中。`ROOT` 是为教学假设的项目根目录；为让示例中的相对路径和错误消息稳定，下面统一用斜杠写路径，例如 `/work/project`，这不是仓库里的真实路径。源文档包含一个指向目标文档第二个 `Setup` 标题的链接：

```markdown
<!-- 假设文件：ROOT/docs/start.md -->
参阅[设置指南](guide.md#setup-1)。

<!-- 假设文件：ROOT/docs/guide.md -->
# Café, Tea!
## Setup
## Setup
## Setup
### API_v2
```

链接目标 `guide.md#setup-1` 由两部分组成：文件名 `guide.md` 和井号 `#` 后的片段 `setup-1`。片段是链接中用于指向文档内部位置的文本。源文档和目标文档同目录，所以这个相对文件名从 `docs` 目录解析到 `ROOT/docs/guide.md`。这里预期的结果是：检查器把标题转换成标识集合，找到 `setup-1`，然后继续检查；如果把链接改为不存在的 `setup-9`，检查器会报告错误并停止当前这次发布检查。

读完本课，你应能沿着这条具体路径解释：目标文字怎样被拆成路径和片段、目标文件怎样定位、标题怎样生成标识、重复标题怎样编号、谁检查成员关系，以及错误怎样影响调用方。本文不要求你先懂 Python、正则表达式、文件路径或 URL。

### 2. 系统位置与架构分工

#### 从脚本入口走到链接检查

`scripts/validate.py` 是发布前检查仓库文件的 Python 脚本，不负责网页导航。文件末尾只有在脚本被直接运行时才调用 `validate()`；后续章节只沿这次调用的一条本地链接往下走。[入口在固定提交原行 121–122](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L121-L122)。

#### `validate()` 为什么持有文件和文本

`validate()` 先确定要检查的文件集合 `files`，再把文件内容读进 `texts`。`UTF-8` 是 `8-bit Unicode Transformation Format`（八位 Unicode 转换格式）：它把 Unicode 文字编码为字节以便存入文件，再把读出的字节还原为文字。一个字节由 8 个比特（0 或 1）组成，一个字符可能需要多个字节；本脚本用 UTF-8 读取，才能把 `Café` 这样的内容还原成字符串。`Path` 是代表文件系统位置的对象，不是文件内容。`texts` 用路径对象作键、文本字符串作值，因而稍后可以用已解析出的目标路径取回目标内容。[固定提交原行 43–53](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L43-L53)。

每轮链接循环里，当前文件路径 `path`、当前正文 `content` 和给错误消息用的相对路径 `relative` 已由外层绑定；目标循环再把一个目标放到 `target`。这些不是标题转换函数的输入。`validate()` 持有它们，是因为它必须把链接文字、文件清单和已读内容连接起来：先定位目标文件，再取出该文件正文，最后检查片段。

#### `heading_ids()` 为什么只收正文

`heading_ids(content)` 只接收一段文本并返回标题标识集合。它不自己打开文件，也不接收来源路径或链接片段。这样标题规则和文件读取分开：调用方负责取得正确文本；标题函数只根据给定文字算结果。维护者若要检查一种标题文字怎样转换，可以把该文字单独交给这个函数推演；文件定位错误仍由调用者处理。这个边界让文本转换不依赖磁盘读写，便于独立核对输入和输出；这里说明的是由函数接口带来的能力，不声称仓库已有专门测试。[函数在固定提交原行 31–39](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L31-L39)。

#### `check()` 把条件交回调用链

在原行 69，`check` 接收“目标是否在发布文件集合里”的真假结果和文件错误消息；在原行 71，它接收“目标片段是否在标题集合里”的真假结果和锚点错误消息。条件为真时，`check` 不抛出异常，调用者可以走到下一条语句；条件为假时，它抛出带有调用者消息的 `ValueError`，这是 Python 内置的异常类型，本例用它表示链接没有通过检查。异常是打断正常语句顺序的错误信号，传播方式在第三章展开。这个函数不打印消息、不改文档，也不替调用者选择继续还是退出；异常沿 `validate()` 调用链传播，脚本入口没有在这条路径上捕获它。[检查函数原行 21–23](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L21-L23)；[调用现场原行 64–72](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L64-L72)。

#### 状态在什么时候存在

一次 `validate()` 运行时，`files` 和 `texts` 为这次检查提供文件清单与文本；目标循环依次处理各个 `target`，成功处理后才在原行 72 增加 `links`。每次 `heading_ids` 调用会重新建立自己的标题列表、计数字典和标识集合。`return ids` 把标识集合交回调用方，供这一次 `fragment in ids` 判断；标题列表和计数字典留在函数内部。它们都是内存中的本次调用状态，不会写回文件，也不会保存到下一次脚本运行。若锚点检查抛错，行 72 尚未执行；本次调用会退出，未交出的局部值随函数退出而不再供后续目标使用。

### 3. 读懂本课所需的概念

#### 函数先定义，再由调用提供输入

Python 文件是一串交给解释器按顺序执行的语句。函数是有名字、可重复调用的一组语句。`def heading_ids(content):` 建立这个函数，**但不会在定义时处理标题**；真正调用 `heading_ids(texts[destination])` 时，Python 才先取出括号里的正文，再开始执行函数体。`content` 是形参，也就是定义里接收输入的名字；`texts[destination]` 是实参，也就是这次调用实际交来的值。形参绑定到实参后，函数内部通过 `content` 读到那段正文。

作用域是一个名字可以被代码直接使用的范围。`content`、`headings`、`slug` 是这次 `heading_ids` 调用里的局部名字；函数外不能直接读它们。函数可以通过 `return` 把指定结果交出去，调用方再把结果存入自己的名字。缩进表示哪些语句属于函数、循环或条件分支；冒号开启一个缩进块。第 39 行的 `return ids` 位于循环之后，所以循环处理完才交回集合。

#### 导入模块，让当前文件能使用工具

`import re` 运行时会把 Python 标准库里的正则表达式模块绑定到当前文件可用的名字 `re`。模块是一组相关工具；`re.findall` 表示从 `re` 模块取出 `findall` 工具，点号把名字和模块里的工具连起来。标准库是 Python 随附的常用模块集合，不需要项目另写这段匹配逻辑。脚本也导入 `Path` 和 `unquote`（原行 7–8）：`Path` 创建路径对象，`unquote` 解码百分号编码。导入只让这些名字可用，不会自动调用标题函数。

#### 用字符串和正则模式寻找标题

字符串是程序中的一段文字，例如 `"## Setup"`。正则表达式是描述文字形状的模式，`re` 模块按这个模式扫描字符串。标题模式是 `r"^#{1,6}\s+(.+)$"`：`r` 让 Python 把反斜线原样交给正则规则；`^` 找字符串开头，启用 `MULTILINE` 后也找每一行开头；`#` 是字面井号，`{1,6}` 表示前面的井号重复一到六次；`\s+` 要求一个或多个空白；`(.+)` 用括号捕获至少一个字符，`.` 默认不跨换行，`+` 表示一次或多次；`$` 找字符串结尾或其最后换行之前，启用 `MULTILINE` 后也找各行结尾。`findall` 按顺序收集括号捕获的文字。

另一条模式 `r"[^\w\s-]"` 用于删除标题中的字符：方括号表示一个字符集合，开头的 `^` 表示“不属于集合”；`\w` 是字母、数字或下划线，`\s` 是空白，放在末尾的 `-` 表示字面连字符而不是范围。此处的 `^` 在方括号外表示行首，方括号内则表示排除；位置不同，含义也不同。`\s` 也匹配换行，因此一行只有 `#`、下一行写 `Next` 时，`\s+` 可能跨过换行并捕获 `Next`；这条规则只是在文本中找形状，不是完整的 Markdown 标题解析器。

模式里的 `\w` 在 Python 默认 Unicode 字符串模式下匹配字母、数字和下划线，`\s` 匹配空白。`MULTILINE` 让 `^` 和 `$` 分别把每一行当作边界；`DOTALL` 会让点号也能匹配换行，本例没有启用它。`ASCII` 是 American Standard Code for Information Interchange（美国信息交换标准代码），这里的 `a-zA-Z` 只接受 ASCII 英文字母；链接前缀检查故意不使用所有 Unicode 字母。`slug` 在本文指由标题文字算出的短标识，例如 `Setup` 会变成 `setup`；它不是 Markdown 各平台共同规定的名字。

#### 标题文字、Unicode 和容器各自保存什么

Unicode 是让不同语言文字用统一字符编号表示的标准。`Café` 中的 `é` 若存成一个预组字符，会被 `\w` 保留；也有人用字母 `e` 加一个单独的组合重音符表示相同外观。当前模式会删掉不属于 `\w` 的组合重音符，因此两种写法可能分别产生 `café` 与 `cafe`。代码没有把这两种编码形式先统一，这就是此处的规范化限制。字符串方法会产生新的字符串，不会在原字符串内部改字。

标题提取先得到列表 `headings`，例如 `['Café, Tea!', 'Setup', 'Setup', 'Setup', 'API_v2']`；列表能保留出现顺序，所以第二次 `Setup` 可被识别为第二次。字典 `counts` 把基础名字映射到出现次数，例如处理三个 `Setup` 后是 `{'setup': 3}`。集合 `ids` 保存最终可查的名字，例如 `{'setup', 'setup-1', 'setup-2'}`；它去重，不记录插入顺序。三种容器不能互相替代：列表给处理顺序，字典记次数，集合用于回答“是否存在”。`API_v2` 只是本课的一个普通标题字符串，计算结果为 `api_v2`；这里没有调用任何项目 API。

`counts.get(slug, 0)` 在键不存在时给默认值 0。`count = ...` 让局部名字指向读出的旧整数；后续 `counts[slug] = ...` 改字典，`ids.add(...)` 改集合。这是重新绑定一个名字与修改已有容器的区别。表达式是一段能算出值的代码：`count == 0` 得到真或假，`fragment in ids` 得到成员检查结果；这两种比较会返回布尔值 `True` 或 `False`，`bool` 是它们的类型名。`if` 和条件表达式也能接收其他类型的值，再按真假判断：非空字符串为真，空字符串为假，数字 `0` 和 `None` 也是假。因此原行 68 的 `if filename` 与原行 70 的 `if fragment` 检查字符串是否非空，并不要求它们本身是布尔值。

#### 路径、URL 与目标文字的三段拆分

`URL` 是 Uniform Resource Locator（统一资源定位符），完整的网址通常还会包含用来定位网络服务的前缀和主机位置。本课里的 `guide.md#setup-1` 没有网址前缀或主机，是从当前文档出发的相对链接目标；`#` 后的 `setup-1` 是目标文档片段。`https:` 是安全网页传输地址常见的 scheme（处理方式前缀），`mailto:` 是邮件地址常见的 scheme；代码只用冒号前的前缀识别并跳过这些目标，不访问它们。

`str.partition('#')` 在第一个井号处切开，并给出固定三项的有序元组：分隔前的文本、分隔符、分隔后的文本。元组是一组有顺序且数量固定的值，因此 `guide.md#setup-1` 得到 `('guide.md', '#', 'setup-1')`。左侧的 `filename, _, fragment` 同时接收这三项；`_` 在 Python 里仍是普通名字，这里表示分隔符接到后不再使用。若目标是 `#setup-1`，文件名前半段为空，表示当前文件中的片段。

`unquote` 把 `%20` 这类百分号后跟十六进制数字（`0`–`9`、`A`–`F`，小写 `a`–`f` 也可）的编码还原为文字；它不联网，也不会把 `+` 当成空格。`Path` 路径对象代表文件系统位置，与保存路径文字的字符串不同：`path.parent / filename` 把目标文件名接到源文档目录后，`.resolve()` 得到绝对规范路径并处理 `.`、`..` 等路径部分，`.suffix` 读取后缀名并保留前面的点号，例如 `.md`；`destination in files` 再检查目标是否属于发布文件集合。

#### 返回、None 与异常怎样改变顺序

调用一个函数时，运行环境会记住当前函数做完后要回到哪一处；这份“谁调用谁、完成后返回哪里”的记录叫调用栈。例如 `validate()` 调用 `heading_ids(...)`，后者执行 `return ids` 后，调用栈让程序回到 `validate()` 继续算 `fragment in ids`。`check(...)` 是另一次函数调用。

`True` 和 `False` 是布尔类型的两个值，分别表示真和假；原行 71 的 `fragment in ids` 会算出其中一个值。`check` 在条件为真时跳过错误分支，然后走到函数末尾。没有显式 `return` 的函数会正常返回特殊值 `None`，意思是“没有交回具体结果”，它不等于 `False`。调用者在这里不靠返回值判断是否成功，而是看 `check` 有没有抛异常。

异常表示正常语句顺序被打断。`raise ValueError(message)` 创建并抛出携带消息的错误；若当前调用链没有捕获它，程序就沿调用栈退回调用者，当前函数后面的语句不再执行。本脚本入口直接调用 `validate()`，本课这条路径没有捕获该错误，因此失败会退出这次检查，不是浏览器跳转或网络错误。

### 4. 端到端流程与本课边界

先把同一组假设值放在一起：当前 `path` 是 `ROOT/docs/start.md`，`relative` 是 `docs/start.md`，`content` 含有上面的链接，`target` 是 `guide.md#setup-1`，`files` 含有 `ROOT/docs/start.md` 和 `ROOT/docs/guide.md`，`texts` 保存了这两份文件的字符串内容。

真实处理顺序是：

1. `local_targets(content)` 发现 `guide.md#setup-1`；本课不把它的正则实现当成标题解析器。
2. `re.match` 看到目标没有 `scheme:` 开头，所以它不是此处跳过的外部链接。
3. `target.strip("<>")` 去掉包在目标外侧的尖括号；`unquote` 解码百分号编码；`partition("#")` 得到文件名 `guide.md`、分隔符 `#` 和片段 `setup-1`。
4. 从源文档的父目录拼出 `ROOT/docs/guide.md`，`resolve()` 规范路径；第 69 行确认它确实属于 `files`。
5. 目标后缀是 `.md` 且片段非空；脚本把 `texts[destination]` 传给 `heading_ids`。
6. `heading_ids` 返回集合。若 `setup-1` 在集合里，`check` 正常结束；若不在，`check` 抛出 `ValueError`，当前调用链停止。

这条路径只证明脚本按自身规则核对仓库文件和标题文字。它不会让浏览器跳转、不会请求外网，也不证明任何网页渲染器恰好采用相同的锚点规则。第 69 行先检查目标是否在发布文件集合里；如果文件缺失，错误发生在标题检查之前。

### 5. 真实源码逐段逐行精读

本章先说每段为何出现、输入从哪来，再展示完整的本段职责代码，最后沿实际值解释。代码块里的新增注释只作读码提示；代码后说明负责推导语法和结果，注释不能替代正文。

#### 5.1 `check`：把条件变成失败信号

##### 业务问题与实现思路

标题转换函数只回答“这段正文有哪些标题标识”，不决定某条链接能否通过。调用者先算出目标文件或片段是否存在，再把这个真/假结果和对应的错误消息交给 `check`。分工很小：`check` 只统一处理失败条件，标题函数与路径解析不混进来；条件成立时它自然结束，调用者继续。

##### 完整函数与固定提交位置

`scripts/validate.py` 中的 `check(condition, message)` 完整函数，原行 21–23，固定提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5`：[对应源码行 21–23](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L21-L23)。

```python
def check(condition, message):  # 教学注释：定义接收判断值和错误消息的函数。
    if not condition:  # 教学注释：只有判断值为假时才进入缩进块。
        raise ValueError(message)  # 教学注释：抛出调用方传来的错误消息。
```

##### 原行 21–23：条件成立时继续，失败时抛错

`def check(condition, message):` 定义名字为 `check` 的函数，并声明两个形参。调用者必须提供一个条件值和一个消息值；定义阶段没有开始检查。冒号后的缩进让下面两行属于这个函数体。

`if not condition:` 先读取 `condition`，再由 `not` 把真变假、把假变真。只有结果为真时，才执行下一行缩进的语句。条件成立时这里不会返回 `True`；它只是跳过错误分支，然后函数到末尾正常结束，隐式返回 `None`。

`raise ValueError(message)` 用第二个实参创建错误对象并抛出。`ValueError` 是 Python 标准库提供的异常类型；这里的具体消息由调用方传入。抛出后，`check` 不会执行后续语句，也不会把布尔值交回调用点。调用方是否继续，取决于更外层有没有捕获异常；本链没有这样的捕获。

#### 5.2 `heading_ids`：把标题文字变成可查找的名字

##### 调用现场与输入准备

前一段调用代码先确认目标路径属于 `files`，然后从 `texts[destination]` 取出完整目标正文，把这段字符串作为唯一实参交给 `heading_ids`。本例正文含有 `Café, Tea!`、三个 `Setup` 和 `API_v2`。函数没有路径或片段参数，因此它只计算文本结果；比较 `setup-1` 是否出现仍由调用者负责。

##### 导入模块的源码与固定提交位置

`scripts/validate.py` 中的模块导入 `re`（原行 4），固定提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5`：[对应源码行 4](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L4-L4)。

```python
import re  # 教学注释：导入标准库正则模块，并绑定到名字 re。
```

##### 原行 4：导入后才能用 `re` 名称找到模块工具

`import` 在这里把模块绑定到当前文件可用的名字 `re`；后面的 `re.findall` 和 `re.sub` 通过 `re` 找到模块里的函数。只导入模块不会运行 `heading_ids`；函数要等到调用表达式执行时才运行。

##### 完整标题函数与固定提交位置

`scripts/validate.py` 中的 `heading_ids(content)` 完整函数，原行 31–39，同一固定提交：[对应源码行 31–39](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L31-L39)。

```python
def heading_ids(content):  # 教学注释：定义接收文档文本的函数。
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)  # 教学注释：按行找标题并收集捕获到的文字。
    ids, counts = set(), {}  # 教学注释：分别创建最终标识集合和计数表。
    for heading in headings:  # 教学注释：按标题在文本中的顺序逐个处理。
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")  # 教学注释：小写、删除指定字符、修剪两端空白并替换普通空格。
        count = counts.get(slug, 0)  # 教学注释：读出这个基础名字此前出现次数，首次默认为 0。
        counts[slug] = count + 1  # 教学注释：把已经出现次数写回计数表。
        ids.add(slug if count == 0 else f"{slug}-{count}")  # 教学注释：首次用基础名字，重复项用旧次数加编号。
    return ids  # 教学注释：循环结束后把最终集合交还调用方。
```

##### 原行 31–32：接住正文并找到标题

`def heading_ids(content):` 定义标题转换函数。`content` 是形参，绑定调用时传进来的整篇字符串；这不是文件对象，也不是路径。函数签名只有一个参数，所以函数不会在这里知道源链接里的片段。冒号和缩进表明第 32–39 行属于函数体。

`re.findall(pattern, content, re.MULTILINE)` 在整个字符串里从左到右找所有不重叠匹配。模式的圆括号只捕获标题正文，因此它返回字符串列表。本例的结果是 `["Café, Tea!", "Setup", "Setup", "Setup", "API_v2"]`；井号本身不在捕获组里。`re.MULTILINE` 让 `^` 和 `$` 可在每一行的边界匹配；不带该标志时，`^` 只匹配字符串开头，`$` 匹配字符串结尾或末尾换行之前，因此这份多行正文不会逐行产生五个标题。点号依旧不跨换行，只有 `DOTALL` 才会改变这一点。

##### 原行 33–34：创建两种状态并按原序循环

`ids, counts = set(), {}` 先建立一个空集合和一个空字典，再按位置把它们分别绑定到 `ids` 与 `counts`。空花括号 `{}` 在这里表示字典；要得到空集合必须写 `set()`。`ids` 负责存最终可查名字，`counts` 负责记每种基础名字已经见过几次。它们是本次函数调用自己的可变容器。

`for heading in headings:` 每次把列表中的下一个标题文字绑定到 `heading`，然后执行缩进的第 35–38 行。列表保留标题出现顺序，因而第二个相同标题能看到第一个标题更新后的字典状态。循环结束后，缩进退回到第 39 行的函数体层级。

##### 原行 35：把一条标题逐步变成 slug

先执行 `heading.lower()`，生成小写字符串；本例的 `Café, Tea!` 变成 `café, tea!`，`API_v2` 变成 `api_v2`。这不是原地改写标题，字符串方法给出结果，随后把结果交给下一步。

`re.sub(r"[^\w\s-]", "", ...)` 对每个符合字符集合的字符用空字符串替换，效果就是删除逗号和感叹号。`strip()` 不带参数时去掉字符串首尾空白；它不会压缩中间连续空格。最后 `.replace(" ", "-")` 把每一个普通空格换成连字符。因此 `Café, Tea!` 最终成为 `café-tea`；若标题中间原有两个空格，代码会留下两个连字符。

点号把方法调用接到前一步的返回值上，整行从内到外求值，最后把最终字符串重新绑定到局部名字 `slug`。它没有直接修改 `heading`。此处理规则没有 Unicode 规范化或完整 Markdown 清理，所以“视觉相同”不保证生成相同名字。

##### 原行 36–38：旧计数决定后缀，集合保存可查名字

`count = counts.get(slug, 0)` 先读出这个基础 slug 的旧计数；第一次遇到 `setup` 时字典没有这个键，于是 `count` 是 `0`。`counts[slug] = count + 1` 随后把新计数 `1` 写入字典。**后缀使用本轮读出的旧 `count`，不是字典写回的新值**；第一次循环时，`count` 仍然是旧值 `0`。

下一条条件表达式 `A if condition else B` 会按条件选择一个结果。第一次 `count == 0` 为真，所以加入 `slug` 本身；第二个 `Setup` 读到旧 `count=1`，计数表先写入 `2`，然后加入 `f"{slug}-{count}"` 得到 `setup-1`；这里 `f` 前缀让花括号中的 `slug` 和 `count` 被当前值替换。`==` 比较两侧是否相等并产生真假结果，前一行的单个 `=` 则把右侧新次数赋给 `counts[slug]`，二者作用不同；第三个标题读到旧值 `2`，加入 `setup-2`。`ids.add(...)` 改动已有集合。它不返回“是否新加”的结果，也不保留加入顺序。

这两份状态不能混为一谈：字典保存次数，集合保存生成的名字。次数表可以让重复标题逐次编号；集合可以给调用者做成员检查。若只保留集合，第二次遇到 `Setup` 时它已经有 `setup`，但集合无法告诉代码应该接着用编号 1 还是 2。

##### 原行 39：循环结束后交回集合

`return ids` 的缩进位于 `for` 循环之外，所以它只在所有标题处理完成后执行一次。它把集合交还给调用点并结束这次函数执行；`counts`、`headings` 等局部名字不会随返回值一起交出。若输入没有匹配标题，循环执行零次，函数仍返回空集合。

#### 5.3 调用者：从链接目标走到通过或报错

##### 调用现场与输入准备

当前 `path` 是 `ROOT/docs/start.md`，`content` 是源文档正文，`relative` 是供错误消息使用的 `docs/start.md`；外层检查循环在原行 52–53 绑定这些值。`files` 和 `texts` 在原行 43–50 建立，`local_targets(content)` 在原行 26–28 找出当前目标。本例逐个跟踪的 `target` 是 `guide.md#setup-1`，目标文件位于 `ROOT/docs/guide.md`。这里展示从目标循环到片段成员检查的连续责任代码。

##### 完整调用责任与固定提交位置

`scripts/validate.py` 中 `validate` 的目标循环与条件（原行 64–71），固定提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5`：[对应源码行 64–71](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L64-L71)。

```python
        for target in local_targets(content):  # 教学注释：逐个处理当前文档发现的链接目标。
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):  # 教学注释：识别带 scheme: 前缀的目标。
                continue  # 教学注释：跳过此目标并开始本循环的下一轮。
            filename, _, fragment = unquote(target.strip("<>")).partition("#")  # 教学注释：清理外层括号、解码并按首个井号拆分。
            destination = (path.parent / filename).resolve() if filename else path  # 教学注释：相对当前文件目录定位目标，片段链接沿用当前文件。
            check(destination in files, f"Missing/unpublished link: {relative} -> {target}")  # 教学注释：先确认目标是发布文件。
            if fragment and destination.suffix == ".md":  # 教学注释：只对非空片段和 Markdown 文件检查标题。
                check(fragment in heading_ids(texts[destination]), f"Missing anchor: {relative} -> {target}")  # 教学注释：用目标文本生成标识并检查片段成员关系。
```

##### 原行 64–66：逐个取目标并跳过 scheme 地址

`for target in local_targets(content):` 调用提取函数并按返回顺序逐项绑定 `target`。当前源文件内容是 `content`，不是目标文件内容；此时还没查 `guide.md` 的标题。`local_targets` 只从内容里找它认可的 Markdown 链接目标，并会忽略标准三反引号代码围栏与行内代码；它不是浏览器或完整 Markdown 渲染器。

`re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)` 只尝试从目标开头匹配。方括号表示字符集合；第一组允许一个 ASCII 字母，后续 `[...] *` 允许零个或多个字母、数字、加号、点号或连字符，最后要求冒号。因此 `https:` 或 `mailto:` 这样的 scheme 会匹配，普通相对路径 `guide.md#setup-1` 不匹配。这个分支只跳过外部目标，不会请求它们。

命中时，`continue` 结束本轮循环并转到下一个目标，不执行本轮后面的文件和锚点检查。没有命中时则继续处理当前 `target`。`continue` 并不结束整个函数；它只影响最近一层循环。

##### 原行 67：先清理和解码，再按井号拆分

表达式从最里面开始：`target.strip("<>")` 去掉两端属于尖括号集合的字符；它不是一个完整的 URL 解析器。接着 `unquote(...)` 将 `%xx` 编码还原为文本。最后 `.partition("#")` 在第一个井号处分割。对当前目标，这些中间结果依次是 `guide.md#setup-1` 和 `("guide.md", "#", "setup-1")`。

左边的 `filename, _, fragment` 同时接收三元组的三项：`filename` 是 `guide.md`，`_` 接到分隔符 `#`，`fragment` 是 `setup-1`。下划线在 Python 中只是普通变量名；程序员常用它表示这个值之后不需要。若目标为 `#setup-1`，则 `filename` 是空字符串；若没有井号，`partition` 会把整个目标放在第一项，后两项为空字符串。

##### 原行 68–69：相对源文档定位目标并确认发布范围

条件表达式 `A if filename else path` 选择分支：本例 `filename` 非空，于是先读 `path.parent` 得到源文档所在的 `ROOT/docs`，再用路径的 `/` 操作符接上 `guide.md`，最后 `resolve()` 得到 `ROOT/docs/guide.md` 对应的绝对规范路径。如果 `filename` 为空，则该链接指向当前文档，直接使用 `path`。

`check(destination in files, message)` 先计算集合成员测试，再调用 `check`。本例的目标在 `files` 中，所以传入的条件是真，`check` 正常结束。若路径不在发布集合里，条件为假，第一段错误消息会抛出；执行流到此停止，不会继续读取 `texts[destination]`。`f"..."` 是格式化字符串：前缀 `f` 让花括号内的名字替换为当前值，所以这里的 `relative` 和 `target` 会填入源文档相对路径与原始目标文字。

##### 原行 70–71：仅为 Markdown 片段计算标题集合

`if fragment and destination.suffix == ".md":` 的 `and` 从左边先判断；片段为空时，右边不会再决定这个条件。当前 `fragment` 是 `setup-1`，而目标路径后缀是 `.md`，所以进入缩进块。无片段的普通文件链接仍经过上一行的文件存在检查；非 Markdown 文件即使带片段，也不会运行标题提取。

在第 71 行，Python 先计算传给 `check` 的两个实参。`texts[destination]` 按目标 `Path` 键取到目标文档字符串；该字符串传给 `heading_ids`，函数计算集合；`fragment in 集合` 返回布尔值；格式化字符串把源路径和目标拼成错误消息。最后这些值交给 `check`。即使条件为真，消息字符串也在调用之前构造，只是 `check` 不会显示它。

若 `check` 正常返回 `None`，原行 72 随后执行 `links += 1`，也就是把当前链接计数加一并存回去，然后循环继续。若 `check` 抛出异常，原行 72 不执行，当前函数和当前文档循环都不会再处理后续目标。

### 6. 关键机制与官方资料解读

下面用五个实际表达式看库规则怎样作用于本例的具体文字和状态。引用的官方页面都是 Python 3.15 文档；固定提交没有声明项目必须使用 Python 3.15，因此这些链接只说明所引用的语言规则，不证明项目的运行环境或实际执行结果。

#### 6.1 `MULTILINE` 怎样让五行标题都可匹配

原行 32 把整篇 `guide.md` 正文交给 `re.findall`，模式是 `r"^#{1,6}\s+(.+)$"`。字符串前的 `r` 让反斜线原样交给正则引擎。`^` 表示行首，`#{1,6}` 要求一到六个井号，`\s+` 要求至少一个空白，`(.+)` 捕获至少一个字符，`$` 表示行尾。圆括号只包住标题文字，所以后续拿到标题正文，不拿井号。

若不传 `re.MULTILINE`，`^` 只匹配整个字符串开头，`$` 匹配字符串结尾或末尾换行之前；对于有多行标题的这份正文，不能逐行找到五个标题。项目传入该标志后，`^` 和 `$` 也在各行边界匹配；点号仍不跨换行。于是捕获组依次得到 `Café, Tea!`、三个 `Setup` 和 `API_v2`，结果列表保留它们在文档中的顺序。`DOTALL` 才会改变点号能否匹配换行，本行没有使用它。[Python 3.15 `re.findall`](https://docs.python.org/3.15/library/re.html#re.findall)讲捕获组返回值；[`re.MULTILINE`](https://docs.python.org/3.15/library/re.html#re.MULTILINE)与[`re.DOTALL`](https://docs.python.org/3.15/library/re.html#re.DOTALL)分别说明这两个标志的作用。规则适用于这条模式，不代表代码理解了 Markdown 的全部语法。

#### 6.2 一条链式表达式怎样把标题变成名字

原行 35 收到 `heading = "Café, Tea!"`，先运行 `lower()` 得到 `"café, tea!"`。接着 `re.sub` 删除不属于字母、数字、空白或连字符的标点，得到 `"café tea"`；`strip()` 去掉首尾空白（此例没有），`replace(" ", "-")` 把普通空格换成连字符，最后得到 `"café-tea"`。逗号和感叹号被删，重音字母保留。

为看清嵌套调用的先后，下面把项目的一行写成等价的临时步骤；这些变量名是教学展开，不是项目源码：

```python
lowered = heading.lower()
cleaned = re.sub(r"[^\w\s-]", "", lowered)
trimmed = cleaned.strip()
slug = trimmed.replace(" ", "-")
```

Python 先算最内层 `heading.lower()`，把它的结果交给 `re.sub`；替换函数的结果接着交给 `strip`，再交给 `replace`，最后赋给 `slug`。每个字符串方法都产生新字符串，原来的 `heading` 不会被改写。`\w` 在默认 Unicode 字符串模式中包括 Unicode 字母数字和下划线，`\s` 包含空白；`re.sub` 把匹配项替换为空文字。官方对应说明分别见 [`str.lower`](https://docs.python.org/3.15/library/stdtypes.html#str.lower)、[`re.sub` 与字符类](https://docs.python.org/3.15/library/re.html#re.sub)、[`str.strip`](https://docs.python.org/3.15/library/stdtypes.html#str.strip) 和 [`str.replace`](https://docs.python.org/3.15/library/stdtypes.html#str.replace)。

这也说明一个边界：一个 `é` 可以作为单个预组字符，也可以由 `e` 加一个单独的组合重音符表示。两者看起来相同，但本模式会保留前者并删掉后者的重音符，可能分别得到 `café` 和 `cafe`。实现没有先把这两种字符组合规范成同一种写法，因此视觉相同的标题不保证名字相同。

#### 6.3 计数字典和标识集合保存不同状态

开始处理标题前，`counts` 是空字典 `{}`，`ids` 是空集合 `set()`。第一个 `Setup` 变成基础名字 `setup`：`counts.get("setup", 0)` 读出默认值 0，`count` 绑定到 0，随后字典改为 `{"setup": 1}`，集合加入 `setup`。

处理第二个 `Setup` 时，`get` 读出 1；局部名字 `count` 继续绑定这个旧值。字典项被重新赋为 2，并不会回头把局部 `count` 改成 2。条件 `count == 0` 因旧值是 1 而为假，`f"{slug}-{count}"` 拼出 `setup-1` 加进集合。第三个标题再经历 `2 → 3`，新名字为 `setup-2`。因此字典保存“每个基础名字出现几次”，集合保存“调用者能查哪些最终名字”。

`dict.get(key, default)` 在键不存在时给默认值；`set.add(value)` 把值加进集合，已存在的同值不会形成第二份。项目用这两个容器，是因为计数和成员检查是两种不同问题；只剩集合就无法知道接下来该编哪个号，只剩字典则不是要交给调用者做 `in` 检查的最终名字集合。[Python 3.15 `dict.get`](https://docs.python.org/3.15/library/stdtypes.html#dict.get)与[`set.add`](https://docs.python.org/3.15/library/stdtypes.html#set.add)分别说明这两项操作。

#### 6.4 解码文字、分开片段，再定位文件

本例原目标是 `guide.md#setup-1`。为了看出解码的作用，把同一目标改写为 `<guide%2Emd#setup-%31>`：它仍是本例的教学目标文字。`strip("<>")` 先得到 `guide%2Emd#setup-%31`；`unquote` 把 `%2E` 还原为点、把 `%31` 还原为数字 1，得到 `guide.md#setup-1`；然后 `partition("#")` 才按第一个井号给出 `("guide.md", "#", "setup-1")`。项目先解码再分割，后续把前后两段当作路径与片段。

`unquote` 只还原百分号编码，不联系远端地址；它也不会把 `+` 变成空格。`partition` 保留分隔符，并且只按第一次出现的位置切开。接着 `path.parent` 是 `ROOT/docs`，路径运算符 `/` 接上 `guide.md`，`.resolve()` 得到目标路径；`destination in files` 检查该路径是否属于本次发布文件集合。空文件名时，条件表达式直接沿用当前 `path`。只有目标在文件集合、片段非空且后缀为 `.md` 时，代码才从 `texts[destination]` 取正文。[Python 3.15 `urllib.parse.unquote`](https://docs.python.org/3.15/library/urllib.parse.html#urllib.parse.unquote)、[`str.partition`](https://docs.python.org/3.15/library/stdtypes.html#str.partition)、[`Path.resolve`](https://docs.python.org/3.15/library/pathlib.html#pathlib.Path.resolve)与[`PurePath.suffix`](https://docs.python.org/3.15/library/pathlib.html#pathlib.PurePath.suffix)分别支持这些操作说明。解码并按井号拆分仍只是本脚本的文字处理规则，不是完整 URL 解析器。

#### 6.5 返回值和异常怎样穿过调用栈

沿真实调用顺序看，`validate()` 先用 `texts[destination]` 调用 `heading_ids`。标题函数完成循环后执行 `return ids`，把集合交回调用点；接着调用者算 `fragment in ids`，再把真假值和错误文字传给 `check`。若成员测试为真，`check` 跳过 `raise`，正常走到末尾并隐式返回 `None`；调用者忽略这个无具体结果的返回值，继续到原行 72 增加 `links`。

若成员测试为假，`check` 执行 `raise ValueError(message)`，本函数此后没有正常返回。异常先退回 `validate()` 的调用位置；由于这条调用链没有捕获它，行 72 和后续目标循环都不会执行。`None` 是正常结束时“没有交回具体结果”的值，`False` 则是一个条件判断结果；二者不能混为一谈。[Python 3.15 `return`](https://docs.python.org/3.15/reference/simple_stmts.html#the-return-statement)、[`raise`](https://docs.python.org/3.15/reference/simple_stmts.html#the-raise-statement)以及[函数正常到末尾时的返回规则](https://docs.python.org/3.15/tutorial/controlflow.html#defining-functions)说明语言层面的控制流。这里的推演来自固定提交源码，不是脚本运行记录。

### 7. 同一组数据的正常与失败回放

#### 正常目标：命中后继续循环

先让 `heading_ids` 处理同一个 `guide.md` 内容。下表按文档顺序计算；计数写成“旧值 → 更新后的值”，所以加入重复编号时使用的是旧值：

| 标题文字 | 基础 slug | `count` 旧值 → 字典新值 | 加入 `ids` 的名字 |
|---|---|---:|---|
| `Café, Tea!` | `café-tea` | `0 → 1` | `café-tea` |
| 第一个 `Setup` | `setup` | `0 → 1` | `setup` |
| 第二个 `Setup` | `setup` | `1 → 2` | `setup-1` |
| 第三个 `Setup` | `setup` | `2 → 3` | `setup-2` |
| `API_v2` | `api_v2` | `0 → 1` | `api_v2` |

函数返回的集合包含 `café-tea`、`setup`、`setup-1`、`setup-2` 和 `api_v2`。集合不保证展示顺序；表格顺序来自输入标题列表，而不是集合。调用方拿到 `setup-1` 后，`fragment in ids` 为真，`check` 跳过 `raise`、正常返回 `None`，原行 72 才把 `links` 加一，然后同一源文件中的下一目标仍有机会检查。假设其余发布检查也通过，脚本会走到正常结束。

#### 失败目标：成员检查抛错并停在行 71

现在只把源文档目标改成 `guide.md#setup-9`。文件路径仍解析到同一个 `guide.md` 并通过文件成员检查，标题函数仍返回同一个集合，但 `setup-9 in ids` 为假。`check` 收到 `Missing anchor: docs/start.md -> guide.md#setup-9`，执行 `raise ValueError(message)`。异常发生在原行 71，因此原行 72 的 `links += 1` 没有执行；当前目标不计作成功，后续目标和后续文件检查也不会在本次调用中继续。

标题函数内部建立的 `headings`、`counts`、`ids` 都是运行时临时数据，返回的集合只用于这次成员判断；这条路径没有任何写文件语句，源文档和目标文档不会被改动。未捕获的异常沿 `validate()` 调用链退回脚本入口，结束本次发布检查。具体错误消息由检查代码构造；本课不推断运行环境怎样显示它。

#### 文件缺失与 scheme 跳过是另一条分支

若路径解析结果不在 `files` 中，先触发 `Missing/unpublished link`，标题函数还没运行。若目标带 `https:` 或 `mailto:` scheme，则 `continue` 跳过本地路径和标题检查；脚本没有验证这些地址是否可用。前者是文件成员条件失败，后者是代码主动跳过，都不代表浏览器行为。

#### 重复标题与自然编号的碰撞

计数器能区分相同基础标题，但不能保证最终字符串唯一。假设目标文件依次还有一个标题 `## Setup-1`：它的小写和清理结果本来就是 `setup-1`，而 `ids` 已经因为第二个 `Setup` 含有 `setup-1`。新标题这轮自己的 `counts["setup-1"]` 从 0 开始，仍会尝试加入同一个名字。集合会把相同字符串合并成一个成员，脚本看不出这两个不同标题发生了碰撞。

这与 `Setup` 重复三次的计数不是一回事：重复计数按基础 slug 记次数；碰撞是两个不同基础来源产生同一个最终字符串。成员检查只回答“集合里有没有 `setup-1`”，不回答它对应哪一个标题。当前脚本因而可能把一个有歧义的片段当成存在。

### 8. 设计取舍与使用/扩展方法

#### 为什么分开读文件、算标题和报告错误

固定提交里的 `heading_ids(content)` 只收文字并回集合，`validate()` 持有路径、`files`、`texts` 和错误消息，`check()` 负责在条件为假时抛错。这是从函数输入、输出和调用位置直接看到的责任边界，不足以证明原作者的主观动机。这样的分离让标题规则可以用给定正文单独推演：例如输入同一段 `guide.md` 正文，可以先检查 `setup`、`setup-1` 是否会生成，不必先打开路径或构造一条链接。它减少了测试标题转换时必须准备的文件系统状态；这是接口带来的便利，不声称项目已经有这类独立测试。

`counts` 和 `ids` 也各有职责。重复的 `Setup` 需要计数器从 0、1、2 生成不同后缀；调用方只需要对最终 `setup-1` 做成员检查。若只保留集合，重复次数消失；若只保留字典，调用方没有最终名字集合可查。这解释了当前两个容器一起出现的具体原因。

#### 轻量标题模式与同一 Markdown 渲染器的取舍

当前模式用行首井号匹配标题，执行简单，但不是完整的 Markdown 渲染器。比如正文中若有以三反引号开头和结尾的围栏代码块，里面写着 `# Setup`，`heading_ids` 仍会把那一行提取成标题；代码没有记录自己是否处于代码块中。另一种 Markdown 标题写法是先写 `Setup`，下一行再用 `-----` 作标记；当前正则要求行首井号，所以不会提取这种标题。标题中两个普通空格也会在替换后变成两个连字符。

若发布规则要求与网站最终显示的标题完全一致，可以选择网站采用的 Markdown 方言和对应渲染器版本，让检查复用相同解析规则。这样有机会减少“检查认为存在、页面却没有该锚点”的差异；代价是要引入并维护同一套解析器、配置和版本约束，而且渲染器升级可能改变已有锚点。这是基于当前边界的设计取舍，不是关于项目实际网站或原作者意图的事实。

#### 修改标题规则会影响已有链接

仅追踪原文中三个同名 `Setup` 对应的计数（下列状态省略 `Café, Tea!`、`API_v2` 等其他标题的字典项）。若把中间第二个标题改为 `Install`，这三个标题的序列是 `["Setup", "Install", "Setup"]`；按此序列更新后，`counts` 依次为 `{"setup": 1}`、`{"setup": 1, "install": 1}`、`{"setup": 2, "install": 1}`，生成名字为 `setup`、`install`、`setup-1`。**原链接 `guide.md#setup-1` 仍会通过成员检查，却会匹配第三个 `Setup`，而不是改名前的第二个标题**；若要继续指向改名后的第二个标题，应把链接片段改为 `#install`。修改大小写或字符清理规则也可能改变旧名字，因此任何转换规则变更都应先列出受影响的现有标题与链接，再一起迁移。

重复基础名的计数并不能解决不同标题产生同一结果的情况：已有两个 `Setup` 时再加 `Setup-1`，依然会产生相同的 `setup-1`。一种扩展设计是在加入候选名字前查 `ids`，若已占用就继续找下一个空名字；当前函数没有此步骤，也不会报告这种碰撞。增加该行为会改变过去可接受的名字，必须同时评估旧链接的指向和迁移方式。

#### 日常编辑如何进入发布检查

维护者编辑 `ROOT/docs/start.md` 的链接，或编辑 `ROOT/docs/guide.md` 的标题；脚本下一次读取这些文件时，会按固定规则重新计算目标和标题集合。成功检查只说明目标路径和片段满足脚本规则，不会改写任一文档，也不保证浏览器采用相同锚点。若新增语法支持，修改范围至少涉及链接目标提取或标题解析规则，并要拿重复标题、自然碰撞、百分号编码和缺失文件等具体输入核对行为；只改错误消息不会改变检查结果。

### 9. 易混淆点与带答案复习

**为什么 `heading_ids` 不收 `guide.md#setup-1`？** 调用者先把它拆成 `filename="guide.md"` 和 `fragment="setup-1"`，再用 `filename` 找到 `texts[destination]`。标题函数只收到目标正文，所以它能算出标识，却不知道哪条链接正在请求它；成员比较留在 `validate()` 中完成。

**第二个 `Setup` 为什么是 `setup-1`？** 第一次先读旧计数 0，字典随后保存 1；第二次读到旧值 1，字典更新为 2，但局部变量 `count` 仍是 1，于是格式化字符串生成 `setup-1`。第三次才读到旧值 2，生成 `setup-2`。

**为什么同时要 `headings`、`counts` 和 `ids`？** `headings` 是有顺序的列表，保留标题出现次序；`counts` 是字典，记录每种基础 slug 的旧次数；`ids` 是去重集合，供 `fragment in ids` 查询。只留 `ids` 无法知道重复标题的下一编号，只留 `counts` 则没有最终标识集合供调用者检查。

**`MULTILINE` 会让 `(.+)` 跨过下一行吗？** 不会。它只改变 `^` 和 `$` 对每行边界的判断；`.` 是否匹配换行由 `DOTALL` 控制，而原行 32 没有传入它。这样一行中的标题正文会被捕获，下一行仍由另一次匹配处理。

**`ids` 里有 `setup-1`，就能证明它对应第二个 `Setup` 吗？** 不能。若另一个标题本身是 `Setup-1`，它也转换成 `setup-1`；集合只保存一个相同字符串，不记录由哪个标题生成。成员检查会答“存在”，却不能辨认这个名字是否发生碰撞。

**`check` 通过时返回 `True` 吗？** 不会。传入的 `condition` 才是 `True`；`check` 跳过错误分支并走到末尾，按 Python 规则返回 `None`。调用者通过“未抛异常”继续执行原行 72，而不是读取 `check` 的布尔返回值。

**链接检查通过能证明浏览器会定位到第二个 `Setup` 吗？** 不能。这里的证据只到 `setup-1 in heading_ids(texts[destination])` 为真为止；它说明固定脚本自己的标题规则接受这个目标。没有验证浏览器或实际 Markdown 渲染器是否采用同一规则。

### 10. 本课收获、证据边界与下一课

这条真实代码路径的因果关系是：链接提取器给出目标文字，调用方识别外部 scheme、解码并分割片段、相对源文档解析目标路径、确认目标属于发布文件、读取对应文本、`heading_ids` 按行提取标题并转换名字、调用方检查集合成员，最后 `check` 正常返回或抛出异常。标题计数器使重复基础标题逐项编号；集合提供最终成员判断，但无法防止不同来源的名字碰撞。

源码依据固定为提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5` 的 `scripts/validate.py`。官方机制说明链接到 Python 3.15 文档，但仓库没有在本例中声明必须使用这一 Python 版本。所有输入和路径都是静态教学假设；没有运行脚本、验证渲染结果或访问网络。本文没有讲完整的文件发现、其他发布检查或完整命令行。

可以接着读同一文件原行 26–28 的 `local_targets`，追问“它怎样从当前文档中筛出链接目标，为什么代码围栏中的例子会被忽略”；这会继续沿用本课的源文档与目标文档，不需要先读其他项目材料。

## 局部成品摘录：检查失败为何停止调用方

以下保留先前版本中有用的局部讲解，供对照局部来源展开；它不是完整课程，也不代表 v1.10.0 的完整正文布局标准。完整、自足的公开课程示范见上方十章主课。

维护者检查发布文件时，需要“条件符合就继续，不符合就说明原因并停止”。条件是一个可判断真假的值；本例 `True` 表示符合要求、`False` 表示不符合。函数是一段有名称、可被调用的行为，参数是调用者交给它的值。`check` 不修复文件，只决定正常返回还是抛出错误。

返回是把执行结果交回调用方；`None` 是表示没有具体结果的特殊值，不是 `False`。调用栈是运行时保存“谁调用了谁、完成后回哪”的记录；本例错误先向 `check` 的调用者传播，再向更外层传播。

源段：`scripts/validate.py` 原行 21–23，符号 `check`，完整函数，无省略。真实调用者为 `validate`，例如原行 48 的文件软链接检查；上游交入检查结果和错误文字，函数不改变这些值；正常返回 `None`，调用方继续，失败抛 `ValueError`，调用方不再执行下一顺序步骤。此处只展开共同检查函数，文件枚举/软链接识别内部不计本例已教。

原源码摘录，行尾“教学”注释为本例添加：

```python
def check(condition, message):  # 教学：定义两个参数，定义时不执行函数体
    if not condition:          # 教学：不符合要求才进入缩进的下一行
        raise ValueError(message)  # 教学：把原因交给异常，离开正常返回路径
```

| 原行 | 语法、值与因果展开 |
|---|---|
| 21 | `def` 定义函数，`check` 是名称；括号内 `condition, message` 是按位置接收的两个参数，逗号分隔。冒号后的缩进表示函数体。执行定义只建立名称和函数的关联；调用 `check(False, "bad")` 时，才令本次 `condition=False`、`message="bad"` 并进入函数体，不会因看见定义就立即报错。 |
| 22 | `not` 对真/假取反，所以 `not False=True`。`if` 在其条件为真时执行下一级缩进语句；条件为假时跳过该块。本例失败值会进入 23 行，成功值 `True` 则使 `not condition=False`，跳过 23 行，走到函数体末尾。这里没有给变量赋新值，也没有改发布文件。 |
| 23 | `ValueError` 是 Python 内置的值错误类型，`ValueError(message)` 用原因文字构造异常对象；`raise` 抛出该对象，正常顺序执行中断。异常沿调用栈向调用者传播，直到遇到匹配的异常处理或结束该执行。本函数没有捕获，也没有正常返回值；调用方不会收到一个 `False` 再继续检查。 |

Python 语言参考的 [函数定义与 if](https://docs.python.org/3.15/reference/compound_stmts.html) 说明定义和条件块的规则，[raise](https://docs.python.org/3.15/reference/simple_stmts.html#the-raise-statement) 说明异常抛出与传播；本例按已读 Python 3.15 规则解释，没有据此声称目标项目或维护者运行环境已锁定 3.15。正常走到函数末尾返回 `None` 的规则见 [Python 教程](https://docs.python.org/3.15/tutorial/controlflow.html#defining-functions)。这支持上述语句语义，不能证明发布检查已经实际执行。

下面是另标的教学调用，不是源码原文，也不是项目已经运行的结果：

```python
check(True, "bad")
check(False, "bad")
```

第一行把 `True` 交给 `condition`，`"bad"` 交给 `message`；22 行判假，跳过抛错，函数隐式返回 `None`，调用者忽略该返回值后继续。第二行交入 `False`；22 行判真，23 行抛出文字为 `bad` 的 `ValueError`。假设外层没有捕获，第二次调用不正常返回，后续顺序语句不执行。两个调用都不修改任何文件；输出错误文字还是由宿主捕获后怎样展示，须读外层或实际观察，本例不能保证界面展示。

本课只解释“同一检查为何继续/停止”。后续可进入真实 `validate` 调用现场，把文件路径、谓词计算和错误文字串起来；不能从这个片段宣称已教完整发布流程。


## 局部成品摘录：重复标题怎样成为不同锚点

维护者在文档写了两个 `## Setup`，链接 `#setup-1` 应能指到第二个标题。锚点是链接中 `#` 后用于定位文章内部位置的名字。这里的 `heading_ids` 只计算本脚本认可的名字集合，不执行浏览器跳转；Markdown（轻量文本标记格式）渲染器是否使用完全相同规则，还要核对目标平台，不能从本函数断言所有编辑器兼容。

源码依据：本仓库当前 `scripts/validate.py:31–39`，完整 `heading_ids` 函数，无省略。调用者是 `validate` 原行 71：把目标 Markdown 正文 `texts[destination]` 传入，拿返回的集合检查 `fragment` 是否在其中；不在则调用前例的 `check` 抛错。`texts` 是本次运行已读文件内容的字典，`destination` 是目标文件路径，`fragment` 是解析出的锚点；此处只展开标题名字计算，链接解析完整过程另讲。输入是假设正文 `## Setup\n## Setup`，不是实测日志。

原源码摘录，原语句无改写，行尾“教学”注释为本例添加；下面的正文按真实原行详细展开：

```python
def heading_ids(content):  # 教学：定义接收正文的函数，调用时才执行函数体
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)  # 教学：按每行模式提取标题文字列表
    ids, counts = set(), {}  # 教学：分别保存不重复锚点与基础名字已出现次数
    for heading in headings:  # 教学：依次处理每个标题，沿用本次调用的计数状态
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")  # 教学：转小写、删其余字符、去首尾空白并替换普通空格
        count = counts.get(slug, 0)  # 教学：取更新前次数，首次出现按0处理
        counts[slug] = count + 1  # 教学：写回增加后的次数，供后续同名标题使用
        ids.add(slug if count == 0 else f"{slug}-{count}")  # 教学：首次保留基础名字，再次按旧次数加后缀
    return ids  # 教学：全部标题处理后交回集合，不是每轮循环返回
```

原行31定义 `heading_ids`，参数 `content` 接收调用者传来的整篇字符串；此时不读取磁盘，也不调用网络。运行定义不执行函数体，进入调用后才从32行处理输入。

原行32的 `re` 是 Python 正则表达式模块，在本文件原行4导入；正则表达式是一种用模式选择文字的规则。`findall` 找到所有符合模式的内容并返回列表，供后续依次处理。`r` 前缀让字符串中的反斜杠保留给正则解析。模式逐项读：`^` 是行首，`#{1,6}` 要1到6个井号，`\s+` 要至少一个空白字符，`(.+)` 捕获一个或更多非换行字符作为标题文字，`$` 是行尾。`re.MULTILINE` 让行首/行尾作用于每一行；只有一个捕获组，所以得到的是标题文字列表而非带井号整行。本输入得到 `["Setup", "Setup"]`。本规则不是完整 Markdown 解析器，例如没有剔除代码围栏中的伪标题，不能教成全部标准行为。

原行33同时赋两个名字：`set()` 创建不重复元素的集合 `ids`，`{}` 创建键→值字典 `counts`。前者装最终可用名字，后者记每个基础名字出现过几次；它们是函数本次调用的内存对象，不是数据库，也不保存到下次运行。单有集合只能去重，无法告诉第二个标题该加哪个编号，因此这里同时需要计数。

原行34的 `for heading in headings` 从列表依次拿一个字符串放入 `heading`，缩进的35–38行每个标题执行一次。第一次和第二次都拿 `"Setup"`，但字典状态已经不同，所以结果不同；不是并行执行两个标题。

原行35先 `heading.lower()` 转小写得 `"setup"`。`re.sub` 把匹配的字符换成空字符串：方括号是字符集合，开头 `^` 在这里表示取反（与32行方括号外的行首不同）；`\w` 是字母/数字/下划线等单词字符，`\s` 是空白，`-` 在末尾为普通连字符。因此删除其余字符。随后 `.strip()` 去首尾空白，`.replace(" ", "-")` 把普通空格变成连字符。各步返回字符串，链式调用是把前一步结果交下一步，最后赋给 `slug`，不原地改 `heading`。两次本例均得 `"setup"`；如 `"Quick Start!"` 则得 `"quick-start"`，感叹号被删。

原行36 `counts.get(slug, 0)` 按键取已存次数，没有键就用默认值0，不报缺键错误。第一次字典为空，所以 `count=0`；原行37把 `count+1` 写回这个键，字典成为 `{"setup": 1}`。第二次36行读到1，37行写成2。局部 `count` 是更新前的次数，不能把37行的新值误当38行所用的值。

原行38在传给 `.add` 前先算条件表达式：`A if 条件 else B` 在条件为真时取A，否则取B，`==` 比较相等而非赋值。第一次 `count==0` 为真，取 `slug`；第二次为假，`f"{slug}-{count}"` 用花括号插入当前值，拼出 `"setup-1"`。集合 `.add` 将选中的字符串加入 `ids`，所以最终装 `setup` 和 `setup-1`。若省掉分支只加 `slug`，集合会把重复项合成一个，第二个标题的可用名字就丢了。

原行39的 `return ids` 在循环结束后交回集合并结束函数，不是每轮返回；缩进比35–38行浅说明它不在循环体内。调用方原行71用 `fragment in 返回集合` 做成员检查；正常假设 `fragment="setup-1"` 为真，`check` 正常结束，发布检查继续。失败假设 `fragment="setup-2"` 为假，`check` 抛出带目标信息的 `ValueError`；本函数不修链接，不会自动新增第三个标题。若无匹配标题，循环零次，返回空集合，同样交调用方判断。以上都是静态回放，未称真实执行成功。

已读 [Python 3.15 正则文档](https://docs.python.org/3.15/library/re.html) 的模式、findall/sub 与 MULTILINE 说明，以及 [字典 get/集合操作](https://docs.python.org/3.15/library/stdtypes.html)：前者支持32/35行匹配与替换的读法，后者支持36/38行默认取值和集合去重。规则在上述原行映射中消化；它们不证明本脚本实现完整 Markdown 语法，也不证明实际渲染。这里示范的是机制/值/Why/失败一起展开，不要求所有课套这一章法或复制这种表述长度。

## 成品示例：`async` 不会替内部 Promise 自动等待

下面的代码和推演值都是虚构的公开教学示意：它们不是目标项目源码、运行记录或学习者证据。`Promise` 与 `async` 是 JavaScript 例子的具体语义，真实项目要按所用语言解释对应的异步规则。这个例子只回答一件事：函数标了 `async`，是否就会自动等待函数体里调用的 Promise？

先把三个词落到具体值上。Promise（承诺对象）是 JavaScript 用来表示一项结果的对象：它可以仍在等待（pending），可以成功兑现并带一个值（fulfilled），也可以失败并带一个原因（rejected）。`await` 写在 Promise 前面时，会让当前 `async` 函数暂停这一步，等 Promise 成功后把兑现值作为表达式结果；若 Promise 拒绝，`await` 表达式会在当前函数中抛出其拒绝原因，之后的顺序语句停止执行，除非有异常处理。`async` 的规则不同：调用一个 `async` 函数总会得到 Promise，但它不会替函数体内每个 Promise 自动加上 `await`。

本例传给 `Promise.resolve` 的是普通空字符串 `""`，不是另一个 Promise，所以 `createSession()` 立即返回一个已经 fulfilled、兑现值为 `""` 的 Promise。它没有访问网络，也没有真正创建会话；空字符串不是会话编号。

```js
function createSession() { // 教学：定义普通函数；调用它才会执行函数体
  return Promise.resolve(""); // 教学：立即交回一个兑现值为空字符串的 Promise
}

async function send() { // 教学：定义异步函数；每次调用 send 都会得到 Promise
  createSession().catch(() => null); // 教学：给创建结果接一个拒绝处理器，但没有保存或等待新链
  return "sent"; // 教学：把 send 自己的最终值设为字符串 sent
}
```

`function createSession() { ... }` 是普通函数定义；花括号里的语句只有调用 `createSession()` 时才执行。调用时没有传参数，因此函数体无需形参。`return` 把表达式结果交回调用者，结束这次函数执行。这里表达式是 `Promise.resolve("")`：标准库方法接收空字符串，并立即给出已兑现的 Promise。这个教学函数既不发送请求，也不提供可用的会话 ID。

`async function send() { ... }` 定义了另一个函数。`async` 让 `send()` 的调用结果总是 Promise；它不意味着里面的 `createSession()` 自动被等待。函数第一句实际调用 `createSession()`，拿到兑现值为 `""` 的 Promise，再调用它的 `.catch(...)`。点号表示从这个 Promise 上调用 `catch` 方法；括号里的 `() => null` 是箭头函数，没有声明形参，因此不读取 `catch` 传来的拒绝原因；`=>` 后面的 `null` 是它被调用时返回的值。`catch` 只在前一条 Promise 链拒绝时调用这个函数。

`.catch(...)` 自己会返回一个新的 Promise，代表处理后的链。本例上游 Promise 已经 fulfilled，所以拒绝处理器不会运行；`.catch` 返回的新 Promise 最终也会以原来的空字符串兑现。代码没有把这条新链赋给变量、从 `send` 返回它，或对它使用 `await`，因此它的兑现值没有被本例后续代码读取。注意，`.catch` 仍然接上了对上游拒绝的处理；没有被消费的是 `catch` 返回的新链。

最后的 `return "sent"` 属于外层 `send`，与 `catch` 回调的返回值不是一回事。它结束 `send` 的函数体并把字符串交给 `async` 规则包装成 Promise。因此调用 `send()` 得到的是一个以 `"sent"` fulfilled 的 Promise；若调用方 `await send()`，拿到的最终值才是字符串 `"sent"`。内层的空字符串从未成为 ID，也不影响这个返回值。

把当前代码按实际值走一遍：调用 `send()` → `createSession()` 立即返回 Promise(`""`) → `.catch` 接上拒绝处理器但不调用它 → `.catch` 返回一条稍后以空字符串兑现的新链 → 这条链没有被继续读取 → `send` 返回值 `"sent"` → 调用 `send()` 的位置收到 Promise(`"sent"`)。因为示例使用已经 fulfilled 的普通值 Promise，不能据此说创建动作会晚于 `send` 完成；示例里甚至没有网络动作。它只证明 `send` 没有显式等待或使用创建结果。

如果将来把 `createSession` 改成可能拒绝的实现，才会进入假设分支：`() => null` 会运行并返回 `null`，于是 `.catch` 新建的链会以 `null` fulfilled。这个 `null` 只是错误处理链的结果，不是会话 ID；而 `send` 自己的 `return "sent"` 仍然决定它返回的 Promise 值。本例当前没有拒绝，因此不能把这段假设说成已经发生的失败处理。

MDN 的 [async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function) 章节说明每次调用 `async` 函数都会返回 Promise，函数可包含零个或多个 `await`；这对应 `send` 的异步返回规则，并不替缺失的 `await` 补出等待。MDN 的 [Promise.resolve](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/resolve) 章节说明普通非 Promise 值会让返回 Promise 立即 fulfilled；[Promise.catch](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/catch) 章节说明拒绝处理器在前序链拒绝时调用，`catch` 返回新 Promise。本例把这三条规则映射到 `""`、`() => null` 和 `"sent"`，只作静态语义推演；它不能证明任何真实会话创建或网络时序。

## 成品示例：父组件传入的值怎样决定 JSX

下面的组件、props 和界面结果也是虚构的教学示意：不是目标项目源码、浏览器运行记录或学习者证据。React 组件只是讲解界面条件的一种具体材料，真实项目没有前端或使用其他框架时不需要引入它。假设父组件要显示一条状态提示：只有 `thinking` 为真且 `isLoading` 为假时显示传入的文字；同时显示对应的状态标签。

JSX 是 JavaScript 的语法扩展，让代码可以写出类似 HTML 的标记。HTML（HyperText Markup Language，超文本标记语言）是网页常用的标记形式；这里 JSX 看起来像那些标签，但代码中的 JSX 是交给 React 的界面描述，不是 HTML 字符串。Props（properties 的简写，组件属性）是父组件通过子组件标签传给子组件的值；React 调用子组件函数时，会把这些值放在一个对象参数中。下面完整保留父组件调用、子组件定义、分支和所有 JSX 闭合符号：

```jsx
function NoticeExample() { // 教学：父组件函数，负责声明并传入本例的具体值
  return ( // 教学：把下面的子组件描述交给 React
    <StatusNotice
      thinking={true /* 教学：父组件传入布尔值 true */}
      isLoading={false /* 教学：父组件传入布尔值 false */}
      text={'正在整理答案' /* 教学：父组件传入这段字符串 */}
    />
  );
}

function StatusNotice({ thinking, isLoading, text }) { // 教学：React 用一个 props 对象调用此组件，参数解构出三个值
  const isThinking = thinking && !isLoading; // 教学：由两个布尔 props 算出本次渲染的判断值
  return ( // 教学：返回完整的 JSX 界面描述
    <section>
      {/* 教学：条件为真时才把文字段落放进界面描述 */}
      {isThinking && <p>{text}</p>}
      {/* 教学：保留条件成立与不成立时各自完整的标签 */}
      {isThinking ? (
        <strong>正在思考</strong>
      ) : (
        <strong>当前没有思考任务</strong>
      )}
    </section>
  );
}
```

先沿父子调用关系读。假设 React 正在处理 `<NoticeExample />`，它调用 `NoticeExample` 函数；父函数返回一个 `<StatusNotice ... />` 的 JSX 元素描述。`thinking`、`isLoading` 和 `text` 是这段调用现场的三个 props：具体值分别是布尔值 `true`、布尔值 `false` 和字符串 `正在整理答案`。React 接着处理这个子组件时，以包含这三个属性的对象调用 `StatusNotice`。组件不是由父代码直接写成 `StatusNotice(...)` 调用；React 在渲染组件时负责调用函数并读取它返回的描述。

`function StatusNotice({ thinking, isLoading, text })` 的参数是一个对象，并用 JavaScript 的对象解构把其中同名属性分别绑定到局部变量。于是这次调用中 `thinking === true`、`isLoading === false`、`text === "正在整理答案"`。`const` 声明一次赋值后不再重新绑定的局部变量；这句 `const isThinking = thinking && !isLoading` 先检查 `thinking`，为真才计算右侧 `!isLoading`。`!` 把布尔值取反，所以 `!false` 是 `true`；两个真值经 `&&` 得到 `true`，因此这次 `isThinking` 为 `true`。若改为 `isLoading={true}`，则 `!isLoading` 为 `false`，整个结果为 `false`。

`return (` 开始返回 JSX 描述。`<section>...</section>` 是完整的外层标签；`{...}` 在 JSX 标签内容中表示把大括号里的 JavaScript 表达式求值，并把结果放在界面描述中。第一处 `{isThinking && <p>{text}</p>}` 使用 `&&`：这里左侧确定是布尔值。当前 `isThinking` 为真，所以表达式结果是 `<p>` 元素描述，里面 `{text}` 取出父组件给的字符串，最终内容为“正在整理答案”。如果 `isThinking` 为假，表达式结果为 `false`，React 不显示一个写着 `false` 的文本，而是没有这个段落。

第二处 `{isThinking ? (...) : (...)}` 是条件（三元）表达式：`?` 后是条件为真时的结果，`:` 后是条件为假时的结果。当前值为真，所以 React 收到 `<strong>正在思考</strong>` 这一支；若值为假，则收到完整的 `<strong>当前没有思考任务</strong>` 这一支。真、假两侧都需要保留，括号帮助把多行 JSX 归在相应结果里。`</strong>`、`</section>`、`)` 和 `}` 分别关闭标签、返回表达式及条件表达式；它们共同构成可读且完整的 JSX 结构。

把本次具体值从头到尾代入，React 处理 `NoticeExample` → 父组件构造 `StatusNotice` 元素并传入 `true`、`false`、`正在整理答案` → React 以 props 对象调用 `StatusNotice` → `isThinking` 算为 `true` → `&&` 选中段落 → 三元表达式选中“正在思考” → React 消费返回的 JSX 描述。按这些规则演算，预期界面包含“正在整理答案”和“正在思考”。这是静态推演，不代表代码在浏览器中运行或已经观察到画面；示例也没有包含应用入口或挂载配置。

React 官方 [Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx) 章节把 JSX 说明为 JavaScript 内可写 HTML-like 标记的语法扩展；[Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component) 说明父组件把值传给子组件，组件通常从 props 对象中解构；[Conditional Rendering](https://react.dev/learn/conditional-rendering) 说明用 `&&` 和 `? :` 等 JavaScript 条件语法决定哪些 JSX 进入返回描述。本例分别映射到父标签的三个具体值、参数解构、局部布尔结果和两个完整分支。这些通用规则不能证明某个目标项目采用了哪一版 React，也不能证明真实浏览器画面。

## 这些写法必须退修

- “21行定义检查，22行判断条件，23行抛错误”：同义翻译，未解释 `def`/参数绑定/`not`/缩进/异常传播，仍未完成教学。
- “因为 `send` 是 `async`，所以它 await 了创建会话”：错误地把“调用总返回 Promise”说成“函数体自动等待内部 Promise”；本例实际调用 `send()` 得到兑现值为 `"sent"` 的 Promise，空字符串链没有进入 `send` 的返回值。
- 只贴 `createSession().catch(() => null)` 并说“失败时返回 null”：遗漏本例传入普通字符串的 `Promise.resolve("")` 已经 fulfilled，因此当前拒绝回调不会执行；也把回调的 `null` 错当成外层函数返回值或会话 ID。
- 只贴 `{isThinking && <p>{text}</p>}`，却没有给出 `isThinking` 的定义和父组件传值：读者无法知道条件来自哪里、当前真假如何计算，也无法复核最终显示内容。
- 只贴三元表达式真分支，删去 `:` 后的假分支，或裁掉 JSX 的关闭标签和括号：代码不再自足，不能说明条件为假时的完整结果，也无法确认返回结构闭合。
- 贴出 21–23 行后只说“检查失败会报错”：没有代码后逐句展开，即使行范围准确也失败；若把原文改成 `return False` 仍标该范围，也是错误源码。
- “点击按钮会调用 sendMessage，随后服务器收到 question”：若正文没写输入字段怎样交给状态对象、请求体/URL怎样形成及服务端取哪个参数，审核者不能自行补链，必须补正。
- “调用 sendEvent，所以页面先拿到编号”：静态调用可能遇关闭状态提前返回或网络未到达；未展示客户端接收/消费条件不能声称必然结果，末尾“未实测”不能抵消正文断言，必须补正。
- “检查通过：有源码链接、官方链接，作者已自查”：没有实际通读与必要解释，不能声称教材合格。

通读时只靠正文理解正常/失败过程，再核源码事实；自己懂 Python 或能查源码不表示文章已经解释。不需要把本例答案再抄成审查报告，具体缺口直接修正文。

---

## 新主课代码来源与许可证

第6章另有 CPython 2.7.18 标准库源码与文档摘录，来源是 Python Software Foundation 的 CPython 项目；该固定版本的 [`LICENSE`](https://github.com/python/cpython/blob/v2.7.18/LICENSE) 中列有 **Python Software Foundation License Version 2**。下方 MIT 文字只说明此前列出的 AOSA 软件文件，不用于标示 CPython 材料；历史局部读码示例的来源和许可也不因本课新增 CPython 引文而改变。

### CPython 2.7.18 的 Python Software Foundation License Version 2

CPython 2.7.18 的 `LICENSE` 要求在 Python 或基于它的衍生版本中保留此许可协议与 PSF 版权声明；第 3 条还要求随衍生作品提供简要修改摘要。以下保留固定标签中的协议文本和声明。本文摘录 `SocketServer.py` 与 `BaseHTTPServer.py` 的连接构造、请求解析/分派和响应写入片段，并添加中文教学注释；复制的 Python 语句未改写。

```text
PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2

1. This LICENSE AGREEMENT is between the Python Software Foundation
("PSF"), and the Individual or Organization ("Licensee") accessing and
otherwise using this software ("Python") in source or binary form and
its associated documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby
grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
analyze, test, perform and/or display publicly, prepare derivative works,
distribute, and otherwise use Python alone or in any derivative version,
provided, however, that PSF's License Agreement and PSF's notice of copyright,
i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020 Python Software Foundation;
All Rights Reserved" are retained in Python alone or in any derivative version
prepared by Licensee.

3. In the event Licensee prepares a derivative work that is based on
or incorporates Python or any part thereof, and wants to make
the derivative work available to others as provided herein, then
Licensee hereby agrees to include in any such work a brief summary of
the changes made to Python.

4. PSF is making Python available to Licensee on an "AS IS"
basis. PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any
relationship of agency, partnership, or joint venture between PSF and
Licensee. This License Agreement does not grant permission to use PSF
trademarks or trade name in a trademark sense to endorse or promote
products or services of Licensee, or any third party.

8. By copying, installing or otherwise using Python, Licensee
agrees to be bound by the terms and conditions of this License
Agreement.

Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020 Python Software Foundation;
All Rights Reserved
```

固定版本原始许可文件：[CPython v2.7.18 `LICENSE`](https://github.com/python/cpython/blob/v2.7.18/LICENSE)。本协议说明仅覆盖本课摘录的 CPython 标准库材料；AOSA 三份项目软件文件的 MIT 条款见下文，二者不是同一许可。

新主课中的 `server.py`、`plain.html` 与目录索引变体 `server-index-page.py` 摘自 Greg Wilson 所著的 AOSA 章节 [“A Simple Web Server”](https://aosabook.org/en/500L/a-simple-web-server.html)，对应仓库 [aosabook/500lines 固定提交](https://github.com/aosabook/500lines/tree/fba689d101eb5600f5c8f4d7fd79912498e950e2)。该仓库在此提交的 [`LICENSE.md`](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/LICENSE.md) 将软件列为 MIT 许可，将书面材料列为 CC BY 3.0。本文复制并讲解许可下的 `server.py` 与 `plain.html`，并摘录 `server-index-page.py` 的目录索引扩展源码，共涉及三份软件文件；中文讲解是独立撰写的说明，不复制章节段落。MIT 条款全文如下，适用于本课复制的 AOSA 软件代码；本页历史局部例子的许可不因此改变。

```text
MIT License

Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to
 the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
