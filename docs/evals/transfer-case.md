# 文件输出片段

这是维护者用的虚构 Python 3.11 案例，不是学习者任务或安装后运行资源。审读范围仅为下方候选片段所承担的源码保真和教学解释；它不是十章完整课，不要求补写整课。读者此前只学过函数、循环、参数、字符串和字典的基础读法，未学过编码、二进制文件或闭包。请对照完整源码及候选正文判断哪些解释充分、哪些需要修订，给出实际表达式、缺少的解释及正文应修位置；区分事实与教学，不依靠自己的专业知识替正文补步骤。不运行文件写出，也不读取其他维护者材料。

## 源码与定位

完整虚构路径 `/fictional/report-demo/main.py`，版本 `fixture-1`；下方首行为原行1，含空行共24行。主入口 `main` 为原行16–20，核心 `write_report` 为1–7，适配函数 `make_delivery` 为10–13。仅依赖 Python 标准功能。

```python
def write_report(rows, deliver):
    total = 0
    for row in rows:
        payload = row.encode("utf-8")
        total += len(payload)
        deliver(payload)
    return total


def make_delivery(output):
    def delivery(payload):
        output.write(payload + b"\n")
    return delivery


def main(config):
    path = config.get("output", "report.bin")
    with open(path, "wb") as output:
        total = write_report(["é"], make_delivery(output))
    return total


if __name__ == "__main__":
    main({})
```

## 候选教学片段

### 输出路径怎样选出来

原行24把空字典 `{}` 交给 `main` 的参数 `config`。原行17的 `get` 是字典的方法：查键 `"output"`，键存在则返回对应值，键不存在则把第二个参数 `"report.bin"` 作为结果，再把结果绑定给 `path`。本次字典没有该键，故 `path` 是字符串 `"report.bin"`。若传入 `{"output": "saved.bin"}`，同一句得到 `"saved.bin"`，并不会先尝试默认路径。这里只示范键缺失的选择；该语句没有检验用户给的值是否适合做路径。原行18接下来会使用选出的路径。

### 原行1–5：累计本行大小

```python
def write_report(rows, deliver):
    total = 0
    for row in rows:
        payload = row.encode("utf-8")
        total += len(payload)
    return total
```

`rows` 接到列表 `["é"]`，循环本次取字符串 `"é"` 给 `row`；`total` 从0开始。UTF-8（Unicode Transformation Format — 8-bit，8位 Unicode 转换格式）用于这里的编码；`"é"` 编码后是 `b"\xc3\xa9"`，所以 `len(payload)` 为2，`total` 算成 `0 + 2 = 2`。这样就讲清了为何文件里的数据大小不能直接按看到的字符个数计算。

### 原行6–7：交付本行并返回

```python
        deliver(payload)
    return total
```

这一块继续上块同一次循环。`deliver(payload)` 把刚得到的内容交给输出，最终 `output.write` 写下该内容及换行；`with` 结束时文件关闭。可以沿“`write_report` → 输出函数 → 文件”理解这条链，不必在这里再看中间函数。返回的 `total` 是2，它统计每行编码内容，不含输出函数额外写入的换行；一次写出成功的情况下文件是3字节，这是静态推演，未执行。
