# 教学示例与验收边界

[返回 README](../README.md)

以下内容是可阅读的协议示范；示例学习者回答和实验不计入真实 mastery。早期文件流程模拟使用19个源文件的Java+Vue静态fixture，不是大型可运行应用。

## A：第一次在 Java + Vue 项目中学习

用户：“带我深度学习这个项目。”

Agent定位项目根，读指导/依赖/入口，枚举前端、后端、SQL、配置、部署、测试、CI等实际区域，建立双地图和动态路线。未检查部分标pending。创建状态/索引/当前合同与事件；不会一开始输出十页分析。

第一单元可从“点击发送”开始：

```text
Page/Component → API client → HTTP → Controller
→ Service → Storage/Provider → Response/Stream → State → UI
```

这是全景解释后逐层进入的功能，不是默认首轮直接抛出的源码链。先讲业务问题、能力和架构分工，再解释当前功能的概念与短代码；确认题目前置齐备后才可问保存消息与调用供应商失败之间的影响。首轮普通学习请求不以这类预测题收尾。

## B：只凭文件恢复

用户在新会话：“继续学习。”

Agent读取state.awaiting、当前Stage与最近事件，核对相关源码指纹；先判断最新反馈、全景与题目前置讲授范围，适合时才复现原待答题。不问“上次学到哪里”，不因新会话就认为答过了；没有讲过则先解释。若实际教过的知识隔日遗忘或关键基础薄弱，可先问少量主动回忆题。

早期独立新上下文模拟实际读取8份局部记忆，核对7个源码/身份指纹，只更新state/journal。没有旧聊天，也没有代答题目或提升能力。

## C：错误理解与逐轮记录

用户：“所以 Service 主要就是为了代码复用，对吧？”

Agent指出复用可能是收益，当前Service承担业务规则与副作用顺序；再问增加CLI后哪些职责仍存在，以及HTTP错误映射属于哪个边界。根据真实源码讲解，不断言作者意图。

保存question/misconception/gap/teaching事件、纠正依据、原主线返回点、新待答题。若只有AI解释而没有独立新回答，L1仍为L1，误解保持unresolved。用户独立回答迁移问题后才评估变化。

## D：阶段完成

| 条件 | 缺失时 | 有真实证据时 |
|---|---|---|
| 完整主链和重要原理 | 继续追踪或知识绕行 | 记录独立解释/预测 |
| Quiz/Restatement | waiting或补救 | 记录回答、提示与评价 |
| required experiment | blocked，不伪造Verified | 保存预测、实际观察、解释 |
| source/coverage有效 | needs_revalidation或补学 | 逐条对照目标 |
| 技术文章质量 | 修订；缺个人证据则回教学 | 通过后才Stage complete |

学习门禁通过后，自动重新编写问题、系统位置、完整链、源码机制、数据/配置/异常、原理、Why/Alternative/trade-off及个人认知。文章质量检查要求删除聊天后仍可恢复核心理解。

早期D通过分支用独立模拟目录里的seeded证据测试生成15节文章及8项文档门禁；未运行真实实验。它证明文件流程可以演练，不证明学习者真实通过。真实项目必须重新取得真实证据。

## 从阶段到项目完成

所有Stage讲过仍不足以完成项目。主要业务后要审计配置、对象、异常、安全、前端、测试和运行基础设施。最后学习者先冻结自己的设计，再实现并验证代表核心机制的Mini Version，与原设计比较。

只有架构图或伪代码时标design_reconstructed/implementation_pending；无法运行不宣布PROJECT_COMPLETE。

## E：固定会话中的主题收束与显式总结

以下是 v1.1.0 的规则示例与桌面推演，不是已经执行的真实学习实验。

学习者仍在同一个会话，已听完 Service 的职责、调用链和错误边界，但尚未回答 CLI 迁移问题：“这块差不多了，接着看下一块。”

导师在切换前写 `.codelearn/notes/topics/S03-T-service.md`：解释当前源码中 Service 的业务规则/副作用顺序，Controller 的 HTTP 边界、关键方法和数据变化、相关异常、设计理由与替代方案；保存“主要为了复用”的真实误解及纠正，并注明 CLI 迁移题尚待回答。文档首写 draft/unverified，回到源码核对后记录检查范围；L1 不因整理提高，误解不因 AI重写而 resolved。允许按学习者要求切主题，原题作为未解项保存。

随后学习者：“总结当前阶段，详细一点。”

导师立即生成当前 Stage 综合草稿，保留待答题、return_points 和 next_action。必要实验未运行就写未运行，Stage 仍 in_progress；文章自检不能代替实验和复述。回复提供文件链接，而非要求“先通过测验才能总结”。

| 边界情况 | 预期动作 |
|---|---|
| 重要主题已收束，Stage 未通过 | 自动写主题文章，不宣告阶段完成 |
| 同一主题继续展开且无新结论 | 保存事件，不每轮重复重写整篇 |
| 仅解释一个 trivial helper | 默认并入已有记录，不单开长文章 |
| 显式总结，但源码/会话范围不完整 | 写可恢复范围的草稿，列 unknown，不补虚构事实 |
| 自检质量 pass，无真实运行 | 可记录质量结果，不能写 runtime_checked 或提高 mastery |
| 笔记依赖的源码改变 | needs_revalidation，重新核对实际代码 |

## F：初学者默认与图表交付

以下为 v1.2.0 的规则桌面推演，不是新的真实学习效果证明。

用户只说“带我深度学习这个项目”，没有填写背景。导师先解释系统解决的问题和一次实际输入输出，用少量白话节点建立地图，再介绍这个流程需要的入口/业务处理等职责。不直接列 IoC、DTO、SSE 等术语让用户自选；项目真的用到时先讲最小概念、语法或框架机制，再回代码。路线包含所有实际模块、关键基础与后续验证/重建，但每轮只展开一个小目标。

用户会启动项目或已掌握 HTTP，不意味着懂事务、代理和响应式；已有 HTTP 独立证据保留，其余领域仍按初学者讲。教学默认不制造 confirmed gap，不给用户记失败。

需要流程图时使用 ASCII ID 与引号标签，关键代码表达式放标签或图下文字；输出前按图型官方语法自检，有工具时实际解析/渲染。用户报告 syntax error 就先修复原图；新图型版本不明则采用基础图型，不声称所有平台都已验证。

## G：调查/笔记不能代替授课

真实使用反馈出现过这一模式：导师长时间扫描、写详细文章，最后只给技术栈和类名链，要求新手不翻代码复述临时消息 ID/完成回调；用户表示不会，导师只把题目缩成“找两个字段”。这没有补上项目全景，也没有交付题目需要的讲解。

v1.3.0 的处理是先区分“导师已调查”与“实际教给学习者”。普通首次学习时默认先解释一个具体用户问题、系统的业务能力、前后端及模块如何配合，说明后续从功能到源码的顺序；不要求先答局部题。读取范围够支持此课即可停止扩大，取消/拒绝等分支记未来主题。

已有旧状态停在 QUIZ，用户说“先从整体从零讲”时：保存原题为待复习项，清 awaiting，将当前动作改为 TEACH，插入/恢复全景阶段；保留所有旧文章、源码调查和能力证据。不能因为旧文章有效就假定学习者会，也不能出一道更小的字段题让用户继续迷路。之后是否提问取决于具体对话讲授范围与可作答材料，能力门禁不会因暂不答题而被豁免。

## H：源码教学交付门禁验收案例

以下是 v1.4.0 的验收输入与期望行为，用于审查课堂回复；不是已执行的独立模型测试。路径/符号为示例定位，实际使用必须读取目标仓库对应源码，不能照搬或虚构存在。

### H1：初学者继续深度学习

输入：“继续深度学习项目。”状态里全景已在对话讲清，当前目标是“点击提交后请求如何发出”；只有备课记录提到 `ChatInput.handleSubmit`，未实际讲实现。

期望：恢复最新反馈与讲授范围，读取当前真实入口及必要一跳被调方法，在回答展示关键片段。先交代用户操作和前后端边界，再解释事件绑定、参数从何而来、条件分支、状态更新与 API 调用先后。说明返回值/异步处理、结果怎样进入状态并显示、失败时发生什么；尚未展开的后端部分明确待追踪。结尾给下一具体符号及待讲问题（不要求先作答），保存 next_action；没有独立表现不提升 mastery。

不合格：“接着看 ChatInput、Store、API，分别负责输入、状态和网络。”即使路径准确、图画完整，也缺实现教学。全景若只存在 Notes、没有对话讲授，预期应先补全景，不能照状态编号硬进细节。

### H2：讲得太浅且不懂

输入：“讲得太浅、我不懂。”上一轮只有“Controller 收请求，Service 处理业务”的职责表，当前想学一次提交怎么执行。

期望：识别缺少“路由到方法、参数传入、业务调用和结果返回”的实现层，不当作用户答错。暂停旧题，在对话展示真实 Controller 方法和所需调用片段：解释注解/函数语法、请求字段如何成为参数、Service 接收什么并返回什么、异常如何传到 HTTP/流及页面。若首次遇到依赖注入，用当前字段/构造器说明对象由谁提供、何时调用，不泛讲整部框架手册。一个小目标讲清后保存后续符号；未确认框架绑定或异常处理时补读必要代码/官方版本证据，或明确未知。

不合格：把原题改成“找出参数名”，给 Notes 链接让用户自学，或再次保证“之后会深入”却不展示代码。交付自检应拦住这些回复，改写后再记最终讲授范围；无必要前置不设置 awaiting。

### H3：配置或入口文件

输入：“这个配置是怎么生效的？”假设验收夹具确实提供了以下三个片段（仅为示范，不是对真实项目的源码核对）：

```yaml
chat:
  timeout-ms: 3000
```

```java
// ChatClient.java：需核实该实例是否由 Spring 管理
public ChatClient(@Value("${chat.timeout-ms}") long timeoutMs) {
    this.timeoutMs = timeoutMs;
}
```

```java
// ChatClient.java：调用点
return httpClient.sendAsync(request, handler)
    .orTimeout(timeoutMs, TimeUnit.MILLISECONDS);
```

期望讲解：`chat.timeout-ms` 是配置键，`${...}` 按键取值，`long` 是整数类型；Spring 创建该对象时把值传给构造参数并存入实例字段，方法执行时把该字段作为异步请求 Future 的等待上限，单位是毫秒。`return` 交回的是 Future，超时使它异常完成，不保证底层网络请求已被取消；还需找到该实例的注册/创建位置及上层异常消费点，确认是否转为页面错误提示。配置文件是否被当前运行 profile 加载、配置覆盖优先级、缺键时的创建失败策略及是否支持热更新，未查证就列未知，不能仅凭文件名宣称生效。不能把样例构造器直接认作已确认的 Bean 注册。

如果问的是入口文件，同样读取真实启动调用/框架注册位置，区分“声明/注册”和“实际执行”，解释启动后谁被创建、何时接收事件及结果交给谁。无需把整个启动框架一次讲完，但必须教本轮所需机制。

不合格：“这是超时配置，可以控制请求时间。”或“入口文件负责启动项目。”这些职责概述都缺读取者、调用关系和生效过程。

### 共同判定

逐项核对真实片段、初学者桥梁、执行/数据/状态/返回链、前置顺序和事实边界；关键项缺失先改写。源码访问受阻时说明缺哪些证据并保留待教范围，不伪造通过。长链只对当前小目标验收，未展开部分保留 next_action；门禁通过也不意味着用户已经 Applied/Verified。

## I：未教概念与逐句跟读（历史示范）

v1.4.1 的验收示范，以下是假设夹具提供的完整片段，不是实际读取目标项目的报告：

```javascript
function remaining(stock, requested) {
  const next = stock - requested;
  if (next < 0) {
    return 0;
  }
  return next;
}
```

输入：“继续讲这段代码。”旧记录只提过“函数、参数、返回值”，没有明确解释。期望先白话讲问题：“已知现有数量和本次要扣的数量，计算剩余数；本段把负结果转成零。”最少背景是数字运算、条件选择和“把计算结果交回调用处”；主动解释这些内容，不先让用户指出不懂的词。

期望展示的教学注释版如下（实际课堂必须是已读取的源码摘录；这里仍为夹具示范）：

```javascript
// function 声明一个可调用的计算过程；remaining 是名称。
// (stock, requested) 定义两个参数，即调用时接收输入值的名字；逗号分隔它们。
function remaining(stock, requested) { // { 开始函数体，即调用后要执行的语句。
  const next = stock - requested; // const 声明本次不再重新赋值的变量；= 存入右侧结果；- 做减法；; 结束语句。
  if (next < 0) { // if 判断括号中的条件；< 比较大小；条件成立才执行此 { } 中的语句。
    return 0; // return 将数字 0 交回调用处，同时结束本次函数执行。
  } // 关闭条件分支；不是调用结束，条件不成立时还会向下执行。
  return next; // 条件不成立时交回 next 的计算值，并结束本次调用。
} // 关闭函数体；写好定义本身不会执行这次计算。
```

接着解释调用者/时机/状态边界：夹具没有提供调用点，不能断言由按钮、服务或数据库触发；需读取真实调用者后再讲业务触发和结果使用。`remaining(5, 2)` 是为了演示的调用表达式，括号中给出的数字是本次传入值，与定义中的参数名区别开；静态推演依次是 `next=3`、条件不成立、返回 `3`。`remaining(1, 2)` 则得到 `next=-1`、条件成立、返回 `0`，最后的 `return next` 不再执行。这里没有修改外部库存，也没有网络/存储副作用；“返回剩余数字”与“真的把库存写入数据库”不是同一件事。若界面如何显示尚无代码，就明确未知并把调用点/使用者保存为接续目标，不把演示说成项目实际运行观察。

涉及框架或浏览器 API 的实际课不能省略另一层：先解释 API（供项目代码调用的平台接口）提供的能力，再沿实际注册/调用/回调说明何时介入、怎样把值或事件交给项目。不存在这类调用的纯计算片段不虚构平台参与。

不合格：只重复“这是函数，返回剩余库存”；把 `const`、`return`、调用、回调等常见词默认已懂；加“计算一下”这类注释但不解释符号与过程；把仅出现过的名称记为已教；要求用户先列出陌生词。自检必须补齐新术语、逐句注释、过程/效果与概念区别，访问不到调用点时明确范围，不伪造完整链路。

## J：v1.5.0 详细教学验收示范

以下三个完整小课是**公开虚构教学材料**，路径、标识与内容均是假设。示范中的注释为教学添加，不是私人项目摘录；没有运行、部署或真实学习效果证据。实际课堂须读真实源码并用真实源行锚点，不能将这些假设路径当已存在。示范既检查课堂也检查笔记，不能只用关键词出现判通过。

### J1：滚动停止后，提示为什么淡出

本课只解决一个因果问题：滚动时把提示变亮，每次滚动重新计算等待时间，最后一次滚动后等待约 300 毫秒再变淡。不展开整个页面、路由和应用状态库。

先认识三个不同的东西。浏览器把页面元素保存成可读写对象，这种页面结构叫 DOM（Document Object Model，文档对象模型）；本例 `hint` 指向其中的提示元素。元素的 `class` 属性是空格分隔的名字，CSS（Cascading Style Sheets，层叠样式表）按这些名字选中元素并规定外观；名字本身没有“变亮”能力。`hideTimer` 则保存一次待执行工作的编号，在 JavaScript 内存中；它既不是元素也不是 CSS 名称。要取消旧工作，需要这个编号。

“函数”是可以重复调用的一组语句；写定义只是保存做法，执行要等调用。“回调”是在现在把函数交给另一个执行者，让其在事件发生或等待结束后调用。这里有两次交付：注册滚动处理函数给浏览器；滚动发生后再把淡出函数交给计时器。`setTimeout` 是浏览器提供的接口，登记稍后工作并立即返回编号，不在当前函数里阻塞等待。`clearTimeout` 用编号取消尚未执行的计时器。其规则分别见 [MDN setTimeout 的参数、返回值和延迟限制](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout#parameters) 与 [clearTimeout](https://developer.mozilla.org/en-US/docs/Web/API/Window/clearTimeout)。

假设页面先创建提示，随后执行下面脚本；这是明确的演示前提。HTML（HyperText Markup Language，网页标记语言）用标签建立元素：`<div ...>` 开始，`</div>` 结束，中间为显示文字。`id` 是本例唯一查找名；`class` 是样式使用的名字。引号包围属性值，`=` 将值交给属性。

```html
<!-- 教学注释：创建提示元素；hint 是查找用 ID，scroll-hint 是初始样式名。 -->
<div id="hint" class="scroll-hint">正在浏览</div>
```

下面假设片段来自 `demo/scroll.js`；每个重要语句都带解释。

```javascript
// 教学注释：const 给一个不再重新赋值的名字；= 将右侧结果存入该名字。
// document 是浏览器提供的当前页面对象；点号选择它的接口。
// getElementById("hint") 按字符串 ID 找元素，括号表示立即调用，找不到返回 null。
const hint = document.getElementById("hint");
// 教学注释：let 声明以后可改值的变量；null 在此明确表示没有待取消的计时器。
let hideTimer = null;

// 教学注释：function 定义函数，onScroll 是名字；() 不声明参数；{} 包围执行语句。
function onScroll() {
  // 教学注释：if 只在括号内条件成立时执行分支；=== 表示严格相等。
  // hint 找不到时返回，结束这次处理；没有 return 值即返回 undefined。
  if (hint === null) return;
  // 教学注释：classList 是元素 class 名的操作接口；add 添加 active，不替换原名字。
  hint.classList.add("active");
  // 教学注释：编号不是 null 才取消旧计时器；让新一次滚动重新开始等待。
  if (hideTimer !== null) window.clearTimeout(hideTimer);
  // 教学注释：window 是浏览器页面窗口对象，setTimeout 登记稍后工作。
  // () => {...} 创建无参数箭头函数并交给计时器，此刻不执行函数体。
  // 逗号分隔函数与 300 两个输入，300 的单位为毫秒；返回的编号存入 hideTimer。
  hideTimer = window.setTimeout(() => {
    // 教学注释：等待到期后浏览器执行此处；remove 只删 active，保留 scroll-hint。
    hint.classList.remove("active");
    // 教学注释：本次待执行工作已结束，变量回到“没有待取消计时器”。
    hideTimer = null;
  }, 300);
} // 教学注释：函数定义结束，此处本身不代表滚动已经发生。

// 教学注释：把函数值 onScroll（没有调用括号）登记为 scroll 事件处理者。
// 浏览器以后把事件送到 document 时才调用它；当前只做注册，返回 undefined。
document.addEventListener("scroll", onScroll);
```

`===` 比较两个值是否严格相等，`!==` 比较是否不严格相等；这里分别判“元素缺失”和“有旧编号”。字符串由引号包围；分号结束语句。本例两个 if 后不写花括号，只控制紧随的一条语句，不包住后面的全部代码。两个检查不能混为一谈：找不到元素时没有可以改样式的对象；有旧计时器时则要防止旧工作过早删掉类名。滚动回调本可接收浏览器传来的事件对象，本例无需读取它，所以没有命名参数；`hideTimer` 和 `hint` 来自外层脚本变量，不是浏览器作为参数传入。内层箭头函数稍后仍能访问这些外层名字，这种保留外层访问关系的机制叫闭包。它访问的是当前变量，不是另造一份 DOM 或全局状态库。

注册不是执行：`onScroll` 将函数交给浏览器，`onScroll()` 才是现在调用。`addEventListener` 建立事件到函数的联系，不主动制造滚动；本例未请求捕获阶段，也未传其他选项。其登记和回调参数规则见 [MDN addEventListener 的参数与回调](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener#parameters)。

假设 `demo/scroll.css` 提供实际外观消费者：

```css
/* 教学注释：点号在 CSS 表示按 class 名选择，不是 JavaScript 对象成员访问。 */
.scroll-hint {
  /* 教学注释：opacity 控制不透明程度；冒号连接属性与值，0.2 表示较淡。 */
  opacity: 0.2;
}
/* 教学注释：两个 class 选择器连在一起，要求同一个元素同时有这两个名字。 */
.scroll-hint.active {
  /* 教学注释：同一属性在更具体的匹配规则中设为 1，元素完全不透明。 */
  opacity: 1;
}
```

因此脚本并未直接设置亮度，它改变 DOM 的 class；CSS 匹配改变后的名字，才影响外观。`classList` 修改 class 的机制可复查 [DOM Standard 的 classList](https://dom.spec.whatwg.org/#dom-element-classlist)，类名匹配见 [MDN class selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Class_selectors)。本例无动画过渡规则，只有两个透明度状态，不能称“渐变动画”。

静态推演：初始化时 `hideTimer=null`，只有基础类所以较淡。假设第一次滚动在 t=0：加 `active` 变亮，登记计时器 A。t=100ms 又滚动：`active` 已有，仍保留；取消 A，登记计时器 B。t=300ms 是 A 原定时间，已取消不会由 A 淡出。B 最早到 t=400ms 才具备执行条件；执行时删 `active`、编号置空，恢复基础透明度。若只有 t=0 一次滚动，则其待执行工作最早约 t=300ms 执行。300ms 是等待阈值，不是准点保证；当前代码执行、浏览器调度和后台限速等可让它更晚。见 [MDN 延迟超过指定值的原因](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout#reasons_for_delays_longer_than_specified)。这都是示范推导，没有观察真实浏览器。

这段没有网络/存储写入。若脚本先于元素创建，查找会是 null，后续分支会返回；本例前提因此重要，不能凭文件名断言加载顺序。若删掉取消旧计时器的语句，多次滚动后旧计时器可能在新等待结束前删类，破坏“最后一次滚动后等待”的目标。实际项目下一查证点是页面加载顺序、事件绑定位置与 CSS 是否加载，而不是一口气展开全部页面框架。

### J2：配置值怎样到达消费对象

本课的因果目标是“一份配置里的名称，怎样成为服务返回的文字”。以下是假设 **Spring Boot 3.5 系列**示例，已读其对应官方章节；不声称使用者项目也为这个版本，不声称示例部署值生效。Java 是示例语言，Spring 是创建/组织应用对象的框架，Spring Boot 提供启动和配置支持。

类是对象的结构/行为定义；对象是按类创建的一份实际数据与方法。字段是每个对象保存值的位置，方法是对象提供的操作。`BadgeProperties` 定义保存名称的结构，`BadgeService` 是使用名称的对象。“依赖”是某对象工作所需的另一个对象；“注入”是创建者把所需对象传入，不是服务偷偷创建自己的配置副本。框架管理的对象称 bean；字段类型和构造器本身不证明该对象已经注册。

假设所有文件在 `example` 包（组织类名的命名空间），配置为加载到本次应用配置环境的 `application.yml`：

```yaml
# 教学注释：badge 是键前缀；缩进使 name 属于它，完整键是 badge.name。
badge:
  # 教学注释：冒号后是文字值；加载到环境后才可能被后续绑定读取。
  name: 学习沙盒
```

配置绑定是把配置环境的值转存进有类型的对象。这里前缀 `badge` 与字段 `name` 对应完整键，框架利用 setter（写字段的方法）赋值；getter（读字段的方法）返回现值。用 getter/setter 暴露属性的写法叫 JavaBean 属性。相关规则见 [Spring Boot 3.5 JavaBean Properties Binding](https://docs.spring.io/spring-boot/3.5/reference/features/external-config.html#features.external-config.typesafe-configuration-properties.java-bean-binding)。

```java
// 教学注释：package 声明此类属于 example；分号结束声明。
package example;
// 教学注释：import 引用框架的注解类型，导入并不创建/注册任何对象。
import org.springframework.boot.context.properties.ConfigurationProperties;

// 教学注释：@ 给类附加框架读取的元数据；"badge" 指要绑定的键前缀。
@ConfigurationProperties("badge")
public class BadgeProperties { // public 可从其他类访问；class 定义结构，{} 为类体。
    // 教学注释：private 只在此类内部访问；String 表示文字；= 设置初始字段值。
    private String name = "默认名称";
    // 教学注释：方法无参数，返回类型 String；getter 在此为手写，没有生成工具。
    public String getName() {
        return name; // 教学注释：读取这个对象当前字段，交回调用者；不是取配置文件。
    }
    // 教学注释：void 表示不交回结果；String name 声明接收本次传入的文字参数。
    public void setName(String name) {
        // 教学注释：this.name 指当前对象字段，右侧 name 是参数，赋值更新字段。
        this.name = name;
    }
}
```

只到这里仍没有实际注册依据。假设启动类继续明确启用该类型，并提供消费对象的创建方法：

```java
package example; // 教学注释：与另外两类位于同一个包。
import org.springframework.boot.SpringApplication; // 教学注释：引用启动框架的接口类。
import org.springframework.boot.autoconfigure.SpringBootApplication; // 教学注释：引用应用配置注解。
import org.springframework.boot.context.properties.EnableConfigurationProperties; // 教学注释：引用启用绑定类型的注解。
import org.springframework.context.annotation.Bean; // 教学注释：引用声明受管理对象创建方法的注解。

@SpringBootApplication // 教学注释：声明这是 Boot 应用配置，启动时框架处理它。
@EnableConfigurationProperties(BadgeProperties.class) // 教学注释：明确注册并绑定这个属性类型。
public class DemoApplication {
    // 教学注释：static 方法属于类；main 是 Java 启动入口；String[] 是文字数组，args 为启动参数。
    public static void main(String[] args) {
        // 教学注释：立即调用 run，用此类配置和启动参数创建应用上下文（管理对象的容器）。
        SpringApplication.run(DemoApplication.class, args);
    }
    @Bean // 教学注释：框架处理配置时登记此方法产生的 BadgeService 对象。
    // 教学注释：框架按参数类型提供已管理的 BadgeProperties，不是方法自己从 YAML 读。
    public BadgeService badgeService(BadgeProperties properties) {
        // 教学注释：new 创建服务对象，构造器接收同一配置对象；return 将服务交给框架管理。
        return new BadgeService(properties);
    }
}
```

`.class` 在 Java 是代表一个类型的对象，用来告诉框架要处理哪种类；不等于创建一个 `BadgeProperties` 实例。数组符号 `[]` 表示可放多个值；`main` 声明不能证明入口真的已运行，示例只展示启动路径。注册依据是启动处理的应用配置与 `@EnableConfigurationProperties`，服务注册依据是 `@Bean`，不是导入、字段或构造器。启用规则见 [Boot 3.5 Enabling @ConfigurationProperties-annotated Types](https://docs.spring.io/spring-boot/3.5/reference/features/external-config.html#features.external-config.typesafe-configuration-properties.enabling)。`@Bean` 方法参数按类型取容器依赖的规则见 [Spring Framework 6.2 的 Bean Dependencies](https://docs.spring.io/spring-framework/reference/6.2/core/beans/java/bean-annotation.html#beans-java-dependencies)。

```java
package example; // 教学注释：同包内能直接使用本例属性类，无需另外 import。
public class BadgeService {
    // 教学注释：保存一个配置对象引用；final 禁止此字段以后改指向别的对象，不冻结对象内容。
    private final BadgeProperties properties;
    // 教学注释：与类同名且无返回类型的是构造器；new 时调用，接收创建者给的依赖。
    public BadgeService(BadgeProperties properties) {
        this.properties = properties; // 教学注释：左是字段，右是参数；保存引用不是复制配置。
    }
    public String label() { // 教学注释：无参数方法，调用后返回一个文字值。
        // 教学注释：点号找对象方法，() 立即调用 getter；+ 将两段文字连接，return 交给调用者。
        return "当前环境：" + properties.getName();
    }
}
```

静态推演按本例前提：启动入口调用框架；框架登记属性类型，创建对象后字段先有“默认名称”；配置环境中存在 `badge.name=学习沙盒`，绑定将该文字交给 setter；框架把属性对象传给服务创建方法，构造器保存引用。以后某调用者调用服务 `label()`，getter 读取字段，方法返回“当前环境：学习沙盒”。未调用 `label` 就不会因注册自动输出这句话。本例未提供 HTTP 路由/UI 调用者，不能宣称页面显示了它；真实项目下一查证点是服务的实际调用点与返回消费位置。

默认字段值是对象初始化值，不等于当前部署配置。是否加载此 YAML、激活何种配置组合、是否有环境变量/命令行覆盖，要按真实项目确认；本例只作假设。字段可经 setter 改变，但不能据此断言框架会自动热更新。getter 为本例明确手写；真实项目若来自生成器，必须读生成注解/插件及版本，解释生成来源，不用“有 getter”冒称其作者与执行链。

### J3：检索到的文字怎样成为模型输入

本课只解决资料到输入的桥梁。检索是从已有资料中选出相关内容，生成是模型根据输入产出新的回答；两者不是同一步。RAG（Retrieval-Augmented Generation，检索增强生成）把选到的资料放进模型输入，帮助生成时参考。这里不讲向量算法，因为没有展示向量检索，也不把尚未教的 AI 内部记成进度。

假设已有检索步骤交回两个短文本：“借阅期限为 14 天。”“每次可续借 1 次。”问题为“最多可续借几次？”。以下 `demo/prompt.py` 是虚构 Python 演示；Python 用缩进表示函数体，字符串是引号包围的文字，列表是按顺序存放多项值的容器。

```python
# 教学注释：def 定义函数；括号声明两个参数名，冒号后缩进内容在调用时执行。
def build_prompt(question, passages):
    # 教学注释："\n" 是换行字符；点号选字符串方法，join 用换行连接列表中的每段文字。
    # = 把连接结果赋给本次调用的局部名字 context；不修改原 passages 列表。
    context = "\n".join(passages)
    # 教学注释：+ 拼接文字，括号让表达式跨行；先放要求，再放资料，再放本次问题。
    prompt = (
        "只根据资料回答；资料不足就说明。\n资料：\n"
        + context
        + "\n问题：" + question
    )
    return prompt  # 教学注释：把组装后的字符串交回调用者；没有调用模型。

# 教学注释：[] 创建列表，逗号分隔两项；这些是假设检索结果，不是这里生成出来的回答。
retrieved = ["借阅期限为 14 天。", "每次可续借 1 次。"]
# 教学注释：现在调用函数，两个实参依次进入 question/passages，返回值保存为 model_input。
model_input = build_prompt("最多可续借几次？", retrieved)
```

具体推演：参数 `passages` 接收 `retrieved` 中两段已有文字；`context` 成为两行资料；`question` 接收问题文字。最后 `model_input` 是下面的完整字符串，并没有自动发送：

```text
只根据资料回答；资料不足就说明。
资料：
借阅期限为 14 天。
每次可续借 1 次。
问题：最多可续借几次？
```

“提示”即模型本次接收的要求与内容，这里组装结果可作为其输入的一部分。真实应用可能另有消息结构、系统指令、长度限制与供应商请求接口；本片段没有这些代码，调用入口、实际发送和错误消费仍待追踪。不能声称模型已收到或运行成功。

若后来模型生成“每次最多可续借 1 次”，这是根据输入形成的新输出，不是上述函数返回的答案，也不是检索器找到的第三段文字。写“只根据资料”是输入要求，不保证模型绝不会出错；若选到的资料缺少续借规则，组装函数仍只会把现有文字连接起来，不能凭空补正确规定。本课已解释选到文本到提示字符串的过程；检索如何选段、供应商如何接收和生成，都保存具体后续点，不假记已解释内部机制或学习者已掌握。

### J4：中断恢复与笔记对应

假设 E000021 已写完整滚动小课和主题笔记，文件状态为 committed，但 journal 范围为 prepared；中断时没有可见课堂依据。恢复不能将其改为 explained 或 L1，不能因“笔记完整”先考计时器。保留原阶段/ID/独立证据与详细度偏好，当前小目标自然补必要内容；若实际可见回复确已包含注册、取消与 CSS 推演，则以该消息和 E000021 确认实际深度，仍不提升独立能力。

对照笔记时检查 J1 的三个状态载体、注册/执行区别、每个重要语句注释、t=0/100/300/400ms 推演与延迟限制是否保留。只有“浏览器处理滚动，CSS 负责样式”则不通过。J2 不能将构造器等同注册，J3 不能将 prompt 等同模型生成回答。仅 prepared 或文章增加的新准备标未授课；教师遗漏不记学习者失败。本页是人工示范与桌面审阅材料，不是独立模型测试结果。
