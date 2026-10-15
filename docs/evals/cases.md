# 开发试写输入

仅用于维护者开发评测，不是 Skill 运行资源、每课任务或适用技术栈白名单。这三个项目均为 fictional（虚构），没有私有项目、用户学习记录或真实服务数据。它们提供不同职责的有限样本，不能证明普适性。每次只把选定案例的完整段落及公共 Skill 交给作者，不提供维护者答案或其他候选稿。

以下路径都是独立虚构项目的完整路径，文件块从原行1开始，空行也计数；稳定定位采用路径、符号与原行。所列即全部必要项目文件，无省略代码。官方资料允许公开读取，禁止安装依赖、启动服务、浏览器或运行应用测试；只做静态读码教学，演算标为推断。维护者后续可把文件原样放到隔离目录，但本页不要求执行或额外建学习状态。

## A：浏览器表单与请求结果

用户学习请求：

> 我是初学者，只学过变量和普通函数调用，还没学 DOM、事件、Promise 或 async/await。请用这个完整小功能写一节可独立阅读的十章教材：从输入 `tea` 点击按钮，到结果出现在页面，讲清程序怎样交接。再讲一次服务器返回 HTTP 503 时发生什么，以及先搜 `tea` 后搜 `milk`、前一个结果更晚到达时会怎样。不要运行应用，实际未教前置请就地解释。

版本与边界：原生现代浏览器 ES2022、DOM/Fetch Web API，无框架。页面与 `/api/search` 同源；后端不在教学范围，给定 HTTP 200 正文 `{"label":"Tea"}`，HTTP 503 正文任意。另一个正常响应可为 `{"label":"Milk"}`。协议限定成功正文为含字符串 `label` 的 JSON；源码中的错误捕获仍按实际实现解释。页面只展示文字，不使用 HTML 插入。

### `/fictional/browser-search/index.html`

```html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Search demo</title>
<form id="search">
  <label>Query <input id="query" name="query" required></label>
  <button type="submit">Search</button>
</form>
<p id="result" role="status"></p>
<script type="module" src="./app.js"></script>
</html>
```

### `/fictional/browser-search/app.js`

```javascript
const form = document.querySelector("#search");
const input = document.querySelector("#query");
const result = document.querySelector("#result");
const state = { request: 0, label: "" };

function render() {
  result.textContent = state.label;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const request = ++state.request;
  const query = input.value.trim();
  state.label = "Loading";
  render();
  try {
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    if (request !== state.request) return;
    state.label = data.label;
  } catch (error) {
    if (request !== state.request) return;
    state.label = `Failed: ${error.message}`;
  }
  render();
});
```

允许资料：[MDN 事件注册](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)、[默认动作](https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault)、[Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)、[async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)、[textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent)，以及其直接链接的相关 MDN/WHATWG/ECMAScript 章节。浏览器 API 文档是维护时当前版本，不假定某个已测浏览器。

## B：CLI 参数与配置

用户学习请求：

> 我只知道变量与函数，还没学命令行、标准库、配置文件或异常。请写一节完整十章教材，教我从 `python main.py --count 2` 的入口读到终端输出，并解释不传 `--count` 和传 `--count 0` 的差异。配置文件就在下面，不要让我自行补源码；文件打不开时也请说明后果。只静态演算，不执行程序。

版本与边界：Python 3.11 标准库，无第三方包。命令的工作目录设为 `/fictional/repeat-cli`，默认配置相对于工作目录定位。只读取指定配置文件、向终端输出；不写文件、不调用网络。参数允许 `--config` 替换路径。配置格式和完整内容如下。

### `/fictional/repeat-cli/main.py`

```python
import argparse
import configparser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="settings.ini")
    parser.add_argument("--count", type=int)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    try:
        with open(args.config, encoding="utf-8") as source:
            config.read_file(source)
        raw = args.count if args.count is not None else config.get("repeat", "count")
        count = int(raw)
        if not 1 <= count <= 5:
            raise ValueError("count must be between 1 and 5")
        word = config.get("repeat", "word")
    except (OSError, UnicodeError, configparser.Error, ValueError) as error:
        parser.error(str(error))
    print(" ".join([word] * count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `/fictional/repeat-cli/settings.ini`

```ini
[repeat]
count = 3
word = hello
```

允许资料：Python 3.11 官方 [argparse](https://docs.python.org/3.11/library/argparse.html)、[configparser](https://docs.python.org/3.11/library/configparser.html)、[内置函数](https://docs.python.org/3.11/library/functions.html)、[异常](https://docs.python.org/3.11/library/exceptions.html)、[__main__](https://docs.python.org/3.11/library/__main__.html) 与直接相关语言参考；维护时网页当前标记3.11.17，案例语言目标仍是3.11。

## C：只读 Go HTTP 服务

用户学习请求：

> 我是初学者，只知道变量和普通函数，不懂 Go 的多返回值、HTTP、环境变量或 handler。请写一节完整十章教材，从程序启动讲到 `GET /double?n=7` 的状态和正文，再讲 `n=bad`、`n=21` 以及 POST 同一路径。环境变量 `MAX_N=20`；请另说明没设置和设置为 `oops` 的启动差异。不要启动服务或执行测试，必要前置就地教。

版本与边界：Go 1.23.0 标准库，单文件，无第三方依赖，无需 go.mod。只监听固定本机回环地址，处理整数计算，不读写业务文件、不调用外网。源码是教学用的小服务，不附加生产部署或认证任务。HTTP 请求和配置均为给定静态输入。

### `/fictional/double-service/main.go`

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
    "strconv"
)

func main() {
    raw := os.Getenv("MAX_N")
    if raw == "" {
        raw = "10"
    }
    max, err := strconv.Atoi(raw)
    if err != nil || max < 1 || max > 100 {
        log.Fatal("MAX_N must be an integer between 1 and 100")
    }
    mux := http.NewServeMux()
    mux.HandleFunc("/double", func(w http.ResponseWriter, r *http.Request) {
        if r.Method != http.MethodGet {
            w.Header().Set("Allow", http.MethodGet)
            http.Error(w, "GET required", http.StatusMethodNotAllowed)
            return
        }
        n, err := strconv.Atoi(r.URL.Query().Get("n"))
        if err != nil || n < 0 || n > max {
            http.Error(w, "n out of range", http.StatusBadRequest)
            return
        }
        w.Header().Set("Content-Type", "text/plain; charset=utf-8")
        if _, err := fmt.Fprintf(w, "%d\n", n*2); err != nil {
            log.Print(err)
        }
    })
    log.Fatal(http.ListenAndServe("127.0.0.1:8080", mux))
}
```

允许资料：Go 1.23.0 官方 [net/http](https://pkg.go.dev/net/http@go1.23.0)、[strconv](https://pkg.go.dev/strconv@go1.23.0)、[os](https://pkg.go.dev/os@go1.23.0)、[fmt](https://pkg.go.dev/fmt@go1.23.0)、[log](https://pkg.go.dev/log@go1.23.0)，及官方 [语言规范](https://go.dev/ref/spec) 的相关小节。若固定版本页面访问失败，可查同 API 当前官方页并明确版本证明边界，不能声称已核完整历史实现。
