# Mermaid 官方语法与输出检查

适用于聊天、项目地图、主题/阶段 Notes 中所有 Mermaid 图。图是帮助初学者理解的模型，不替代机制解释；每张图说明起点、箭头含义和当前省略的细节。

## 官方依据与兼容范围

使用 [官方语法总览](https://mermaid.js.org/intro/syntax-reference.html) 和对应图型文档：[流程图](https://mermaid.js.org/syntax/flowchart.html)、[时序图](https://mermaid.js.org/syntax/sequenceDiagram.html)、[类图](https://mermaid.js.org/syntax/classDiagram.html)、[状态图](https://mermaid.js.org/syntax/stateDiagram.html)、[ER 图](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)。不得把一种图的节点/箭头语法混入另一种图。需要新图型或不确定写法时查官方对应页，不猜语法。

先判断目标渲染器支持的图型/版本；未知时默认传统 flowchart 或 sequenceDiagram 的基础语法，避免新版本 shape、图标、Markdown 标签、HTML 换行、布局插件和初始化指令。合法的新语法也可能不被旧渲染器支持，不宣称跨所有平台可渲染。

## 默认保守写法

- Markdown 使用独立的 mermaid 代码围栏，第一行声明图型；围栏内只放图代码，每个声明/连线单独一行。
- Flowchart 的节点 ID 用稳定 ASCII，如 N1、N2、SG1；先定义节点再连线，中文、函数括号、路径、泛型等只放双引号内的显示标签，例如 `N1["接收请求：handle(input)"]`。显示标签与 ID 分开，不要把源码表达式直接用作 ID。
- 标签内需要双引号时用官方实体转义（如 `#quot;`），不要假定反斜杠转义有效。竖线/引号等可能冲突的边标签优先改成短白话；复杂代码移到图下文字。默认单行标签，避免嵌套括号、HTML 或 Markdown 引起额外兼容问题。
- Flowchart 用传统 `-->` 连接，边标签默认用双引号包裹，例如 `-->|"成功"|`；含函数括号、方括号、泛型、引号或竖线等不要裸放，内部冲突字符按上一条转义或改短白话，复杂代码放图下解释。此规则只用于流程图边标签，不套到时序图消息语法。避免以裸小写 end 为节点 ID/显示标签；子图的 `end` 是合法闭合关键字，必须保留。箭头两侧留空格，避免 o/x 与连线组合改变边类型。
- 子图用独立 ASCII ID 与引号标题，逐个闭合；不把 subgraph 写进 sequenceDiagram。时序图先声明 `participant P1 as 用户` 等参与者，消息用该图型的 `->>`/`-->>`；alt/opt/loop 等块匹配 end，不用流程图的方框语法表示参与者。
- 注释放在独立 `%%` 行。节点/参与者先声明，分支、括号、引号和代码围栏配对；不使用 Unicode 箭头替代图语法。

流程图示例（教学模型，不代表某个项目已验证的实现）：

```mermaid
flowchart LR
    N1["用户提交输入"]
    N2["入口适配：handle(input)"]
    N3{"输入是否有效"}
    N4["核心处理与保存"]
    N5["返回结果并更新界面"]
    N6["返回错误并说明原因"]
    N1 --> N2
    N2 --> N3
    N3 -->|"有效"| N4
    N3 -->|"无效"| N6
    N4 --> N5
```

函数调用作边标签时，错误写法 `H -->|response.json()| J` 会让括号进入流程图语法解析；改为 `H -->|"response.json()"| J`。这组最小对照在 Mermaid 10.9.3、11.4.1实际复现失败/通过；错误示意不放进可渲染 Mermaid 围栏。依据见官方 [特殊字符](https://mermaid.js.org/syntax/flowchart.html#special-characters-that-break-syntax)。

时序图示例（只表达一次请求与响应）：

```mermaid
sequenceDiagram
    participant P1 as 用户界面
    participant P2 as 请求入口
    participant P3 as 业务处理
    P1->>P2: 发送输入
    P2->>P3: 调用处理
    P3-->>P2: 返回结果
    P2-->>P1: 展示结果
```

## 布局与可读性

Mermaid 把边标签居中画在两点之间；标签比相邻生命线或子图边框的间距宽时，一定压线。
语法正确、能出图，不等于读得清。下面几条来自真实渲染对比（同一张图，标签瘦身后压线消失）：

- 时序图消息标签 ≤ 20 个显示宽度（汉字算 2、ASCII 算 1，约 10 个汉字），
  自消息 ≤ 14（约 7 个汉字）。超了就删修饰语，把参数、路径、完整句式移到图下正文。
- 参与者 ≤ 8 个。超过时合并同层参与者（例如把开发代理并进消息标签），或拆成两张图。
- 流程图边标签 ≤ 14 个显示宽度（约 7 个汉字）；跨子图的边尽量不带标签，
  标签只放在同层节点之间的空隙里。
- 节点标签里的长英文标识符会在连字符处断行（`react-\nrouter`）；改用中文别名或缩短。
- 流程图只缩**边标签**；节点与子图标题保留完整名称（`RAGChatServiceImpl.streamChat` 照写），
  节点框会自己变宽，不会压线。
- 时序图标签放不下时按这个顺序处理：**先缩标签 → 再拆成两张图 → 最后才减步骤**。
  不允许为了消压线直接删参与者、节点或步骤；确实要减的细节，必须在图下正文里写全。
- 一张图只讲一条主线：节点 > 20 或子图 > 5 时拆图。

## 输出前门禁与修复

1. 对照本图型的官方语法检查声明、ID/标签、关键字、箭头和块闭合；确认与源码流程一致。图的语法正确不证明业务链正确。
2. 有现成目标预览/解析工具时，对最终完整代码实际检查。官方 [mermaid.parse](https://mermaid.js.org/config/usage.html#syntax-validation-without-rendering) 检查语法时先 `await mermaid.parse(code)`，等待结果或异常，不把Promise对象当成功；`false` 或异常均为失败。成功形态随版本不同：本次10.9.3实测返回 `true`，11.4.1返回含 `diagramType` 的对象，不强制假定所有版本都返回对象。已有 Mermaid CLI/渲染器可检查输出；分别记录语法自检、实际解析与目标平台渲染范围，围栏闭合或链接检查不能证明图语法，解析通过也不等于目标平台渲染通过。

   能装 CLI 时**真的出图再看一眼**，不要只看退出码：

   ```
   mmdc -i x.mmd -o x.png --size 3000 --scale 2 -b white
   ```

   mermaid-cli 12 用 `--size`，旧版的 `-w/--width` 已删除，照旧文档传会报
   `unknown option '-w'`。Windows 上没有 Chrome 时可指向 Edge：
   `PUPPETEER_EXECUTABLE_PATH="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"`。
   出图后目检三件事：标签有没有被生命线或子图边框穿过、长英文词有没有断行、
   箭头是否指向你以为的节点。`audit_lesson.py` 会把超宽标签报成 diagram 告警。
3. 失败时根据实际报错修改原图，重新检查受影响图；先简化标签、ID、块/箭头，不通过更换代码围栏隐藏错误。用户报告 syntax error 时先修复那张图，必要时仅询问缺失的原图或渲染器信息，不让用户自行修语法。
4. 无法实测时仍须逐项自检，只说明“语法自检，目标渲染未实测”；不声称已解析/已渲染。不要为了画图擅自安装项目依赖、修改项目构建或把私人源码/笔记上传在线编辑器。若无法确定合法写法，保留文字流程并说明图待修复，不能交付已知失败的 Mermaid。

文章评审记录 diagram_check（自检/解析/渲染）、工具/版本、检查范围与未测项。图表失败需修复才能通过文章质量门禁；没有图时记 N/A，不为模板强行画图。
