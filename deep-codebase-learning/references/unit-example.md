# 单元示范：从一个真实长课里逐字摘出的两个单元

> **来源与许可。** 摘自 `ragent-official`（Apache-2.0，许可见 [原文](licenses/ragent-Apache-2.0.txt)）的学习笔记 `.codelearn/notes/S00-项目全景/S00-T03-05-队列拒绝与消息增量.md`，仓库 revision `16984b95454d3fc2a55b60ade1950fefeba339ec`。**下面两段是该笔记的原文逐字摘录，一字未改**；摘录只去掉上下文（其余 23 个单元、第一至四章、第六至十章），没有改写、没有补字、没有删句。
>
> **为什么用它当示范。** 用本 skill 的 `audit_lesson.py` 量这份完整笔记：25 个 5.x 单元、165 个源码块、221,831 汉字，`problems` 为 0。下面两个单元在这份笔记里属于块质量最好的一档——每块 50.8–79.0 字/行（无一低于 50），讲解/引用比最低 1.22（无一低于 1.2）。这不是「专家写的范文」，是一份真的按本 skill 合同写出来、并且真的过了门禁的稿子。
>
> **怎么读。** 只读与你当前单元**同类**的那一段，两段不必都读：写后端机制、并发或框架介入时读 A；写前端状态或渲染链时读 B。已读且内容未变就复用，不要为「确认一下」整篇重读。示范尺寸不是课程上限——真实单元按目标源码规模和调用深度定，长职责连续分块并跟完解释。
>
> **摘录里的源码定位。** 原文的每块定位是相对项目 `.codelearn/` 的可点击链接（如 `../../../rag/.../X.java#L176-L181`）。摘录里改成纯文本「文件名 + 原行」：本文件不在那个项目目录下，保留相对链接只会是死链。真实笔记里仍须写成可点击定位，这条合同不因本示范而放宽。
>
> **两段各证明什么。** A 证明「一个机制单元怎么把框架行为剥到底层」：线程池的拒绝策略、分布式许可的两道门、初始化顺序与失败面，每块后面都有框架契约 + 底层/设计两条整组事实。B 证明「一条数据怎么沿渲染链走完」：Store 快照 → 列表项 → 气泡 → Markdown 分支，四处入口各自接在哪。两段都不证明大型仓库的架构覆盖、也不证明学习者已经掌握；它们是写作形状与讲解厚度的参照，不是课程验收结论。

## 5. 两个技术栈的单元示范（节选）

本节只有两个单元，来自同一份真实长课：A 是后端机制单元，B 是前端渲染链单元。两段保持原文的单元标题与七个写作位置，可以逐节对照 [canonical 模板](../assets/templates/stage-note.md#5x-真实符号本单元具体行为)。

### 5.2.1 两道接收门：全局关闭直投有界池，开启后先取分布式许可再交给同一个池

#### 实际问题与实现思路

一次聊天请求不是一次短查询：它要在服务端占住一条 SSE 长连接，向模型供应商发起一次流式调用，再把回复一块块写回浏览器。这个动作既花时间又花配额，所以「让不让他现在开始跑」必须由两个不同的资源来回答。集群整体的并发额度在 Redis 里，一台机器根本看不见别的机器在跑什么；本机能同时跑多少条流，又只有本机知道。只留一道门都不成立：只按本机线程池限制，十台机器就是十份额度，供应商那边的并发和账单先失控；只按分布式许可限制，一次放进来一百个许可，本机的线程、内存和连接会先撑不住。

所以 `enqueue` 里是两道串行的门。第一道看全局开关：关掉限流时，工作直接交给本机执行器，不再去 Redis 取许可；打开时，先把请求交给 `FairDistributedRateLimiter` 排队等一个许可，获准之后仍然要交给同一个本机执行器去跑。这两道门管的不是同一件事：本机池是「执行名额」，它的队列容量是零，接不住就当场拒绝；分布式门才是「等待预算」，请求可以在里面等最多 `maxWaitMillis`。配置里同时存在 `max-concurrent` 和 `max-wait-seconds`，就是因为这两个数字回答的不是同一个问题。

第三个约束来自 SSE 本身：前端正等着事件，服务端不能因为「忙」就把连接静默挂住。直通分支的做法是同步兜底——线程池拒绝会当场抛异常，`enqueue` 在自己的线程上接住它，立刻走拒绝回调。限流分支的做法是把拒绝做成一个 `Runnable` 交给许可器，等排队超时再执行。这里埋着一个后面必须盯住的事实：那个拒绝回调最终是「再次提交」给同一个本机执行器的，池满时它自己也会被拒；所以「请求被拒绝」和「拒绝消息一定送到前端」不是同一件事，本单元剩余部分就是为这个差别准备证据。

#### 架构位置、真实触发与输入准备

本单元涉及的三个对象都是 Spring 单例，在容器启动期间就位。`ThreadPoolExecutorConfig` 是一个 `@Configuration` 类，它的 `chatEntryExecutor` 方法（原行 179–195）返回一个被 TTL 包装过的 `Executor`；`ChatRateLimiterConfig.chatRateLimiter`（原行 33–43）用 `@Bean(initMethod = "start", destroyMethod = "stop")` 造出 `FairDistributedRateLimiter`，并把这个 Bean 挂到容器的生命周期上；`ChatQueueLimiter` 自己是 `@Component`（原行 50），六个 `final` 字段由 Lombok 的 `@RequiredArgsConstructor`（原行 51）生成的构造器注入，其中就有上面这两个 Bean。请求到来时使用的正是这三个已经建好的单例，不会重新建池，也不会重新建限流器。

真实触发链是：浏览器发 `GET /rag/v3/chat?question=请总结这份文档&conversationId=C-100`，`RAGChatController.chat`（原行 51–57）先 `new SseEmitter(...)`，再把 question、conversationId、emitter 交给 `ragChatService.streamChat`；`RAGChatServiceImpl.streamChat`（原行 51–67）看到会话号非空就沿用 `C-100`，生成一个雪花 `taskId`，用 `callbackFactory.createChatEventHandler(...)` 建出本次请求的回调，然后调用 `chatQueueLimiter.enqueue(question, actualConversationId, emitter, () -> traceRunner.run(...))`。第四个实参是一个 lambda，里面装着 `StreamChatContext` 的构建和 `chatPipeline.execute(ctx)`——也就是说 `onAcquire` 代表「整条还没开始跑的业务」，不是它的执行结果。

本单元沿用的样例值：`rag.rate-limit.global.enabled=true`、`max-concurrent=10`、`max-wait-seconds=15`（本仓库 `application.yaml` 原行 105–107），因此池大小是 10，等待预算换算成 `15000` 毫秒；`lease-seconds=30`、`poll-interval-ms=200` 只影响许可租约和轮询节奏。初始状态要记住两点：池里此刻是 0 个线程（没有预热，且允许核心线程超时），Redis 信号量的许可数要等 `start()` 里的 `trySetPermits(...)` 执行过才是 10。值的持有者是两个单例 Bean 和（下一个单元的）每次请求的 `AcquireRequest`/`Ticket`；结果的消费者是 `chatEntryExecutor` 的 worker 线程，它跑完 `onAcquire` 之后由 `SseEmitter` 把事件写回连接。

#### 源码定位与阅读准备

完整路径、符号与原行如下（源码 revision `16984b95454d3fc2a55b60ade1950fefeba339ec`，本地快照，无公开 repo 元数据）：

- 执行器 Bean：`ThreadPoolExecutorConfig.chatEntryExecutor`（`ThreadPoolExecutorConfig.java` L179–L195），原行 179–195，本单元切成两组读。
- 接收门：`ChatQueueLimiter.enqueue`（`ChatQueueLimiter.java` L64–L86），原行 64–86，切两组：直通分支 64–73、全局限流分支 75–86。
- 限流器 Bean：`ChatRateLimiterConfig`（`ChatRateLimiterConfig.java` L31–L43），原行 31–43。
- 限流器构造：`FairDistributedRateLimiter`（`FairDistributedRateLimiter.java` L81–L109），原行 81–109，切三组：81–90、92–97、99–109。
- 配置来源：`RAGRateLimitProperties`（`RAGRateLimitProperties.java` L28–L60）（`@Value` 默认值在第 34、40、46、52、58 行）；运行值在 `application.yaml`（`application.yaml` L103–L109）。
- 下一个单元（5.2.2）才会读的内部位置先记在这里，免得读者以为是本单元漏了：`acquire` 138–151、`Ticket` 字段与构造器 161–172、`timeout` 193–199、`grant` 207–236、`releaseHeldPermit` 241–247、`cleanup` 255–277、`submitSafely` 290–296、`tryAcquireIfReady` 301–336、`scheduleQueuePoll` 338–354、`start`/listener 111–120、`loadLuaScript` 447、`PollNotifier.fire` 517–542。以上行号全部按当前源码核过。

前置概念在这里一次给清，后面不再重复。`IntSupplier` 是 JDK 的函数式接口，唯一方法是 `getAsInt()`：无参、返回 int，所以 `rateLimitProperties::getGlobalMaxConcurrent` 这种「对象 + 方法名」的方法引用能直接当它用；绑定这一刻不调用 getter，只有 `getAsInt()` 被调用时才取值。`SynchronousQueue` 是容量为 0 的移交队列：它的入队只有在恰好有线程正等在那儿取任务时才成功，放不进去就说明没人在等。`AbortPolicy` 是 `ThreadPoolExecutor` 的拒绝策略，触发时构造 `RejectedExecutionException` 并在调用 `execute` 的那个线程上抛出——这就是 `try/catch` 能接住它的原因。`Boolean.TRUE.equals(x)` 里的 `x` 是包装类型 `Boolean`，可能是 `null`；`@Bean` 的 `initMethod` 是 Spring 的生命周期回调名，写法是字符串，拼错不会编译报错。最后，`TtlRunnable` 与 `TtlExecutors` 来自 TransmittableThreadLocal 2.14.5：它们在提交任务时捕获提交线程的 ThreadLocal 快照，在目标线程执行前回放，跑完再恢复。

范围边界也要说清：本单元读到「把 `AcquireRequest` 交给 `acquire`」为止。`acquire` 内部怎么建票据、怎么入队、怎么抢许可、怎么超时，属于下一个单元（5.2.2）；Redis Lua 脚本 `lua/queue_claim_atomic.lua` 内部的排序算法不在本课展开。

#### 4–5 连续源码与紧邻逐行推导

```java
    /**
     * SSE 排队后执行入口线程池
     */
    @Bean
    public Executor chatEntryExecutor(RAGRateLimitProperties rateLimitProperties) {
        int size = rateLimitProperties.getGlobalMaxConcurrent();
```

##### 原行176–181：声明有界执行器 Bean，池大小取自限流配置（`ThreadPoolExecutorConfig.java` L176–L181）

这三行 Javadoc（原行 176–178）编译后不进入执行路径，但它把用途写死在这里：「SSE 排队后执行入口线程池」。「排队后」三个字是本单元的坐标——这个池接的是已经获准的工作，排队本身由另一个组件负责。读源码时不要把注释当运行时事实，但它是判断设计意图的第一手材料。

`@Bean`（原行 179）是 Spring 的注解，标记「这个方法的返回值由容器管理」。容器刷新时调用一次这个方法，把返回值注册成一个单例 Bean，Bean 名默认取方法名 `chatEntryExecutor`。所以这一行不创建线程，也不执行 `new`，它只是把「怎么造」交给容器，由容器在启动期调用下面的方法体。如果这个工厂方法被调两次，就会得到两个互不相干的池——单例语义正是本单元能谈「同一个执行器」的前提。

方法签名（原行 180）把返回类型写成接口 `Executor` 而不是 `ThreadPoolExecutor`，这是刻意的收窄：容器和注入点只承诺「能 `execute`」，后面 `FairDistributedRateLimiter` 拿到的类型也是 `Executor`，谁都 cast 不回池对象去改容量。形参 `RAGRateLimitProperties` 由 Spring 注入，它是一个带 `@Configuration` 和 `@Value` 的配置 Bean，不是这里 new 的。

原行 181 的 `getGlobalMaxConcurrent()` 是 Lombok `@Data` 生成的 getter，字段上的 `@Value("${rag.rate-limit.global.max-concurrent:50}")` 决定它的值：本仓库 `application.yaml` 写了 10，所以 `size` 是 10；只有属性缺失才会落到冒号后的默认值 50。`Integer` 赋给 `int` 会发生拆箱，如果绑定把字段留成 null，这里立刻 `NullPointerException`，启动就失败——这比让池以 0 个线程跑起来要好。`size` 是方法内局部变量，只在建池时用，之后没有任何地方能改它：运行期改配置不会改变已经建好的池。

这里有两件只看这六行看不出来的事。框架契约是：`@Bean` 的方法名就是 Bean 名，这也是后面注入能按名字选中它的依据，改方法名等于改装配规则。设计层的事实是：返回值声明成 `Executor` 而不是具体池类型，让 TTL 包装和内部实现都可以替换，而调用方一行不用改。

```java
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
                size,
                size,
                60,
                TimeUnit.SECONDS,
                new SynchronousQueue<>(),
                ThreadFactoryBuilder.create()
                        .setNamePrefix("chat_entry_executor_")
                        .build(),
                new ThreadPoolExecutor.AbortPolicy()
        );
        executor.allowCoreThreadTimeOut(true);
        return TtlExecutors.getTtlExecutor(executor);
    }
```

##### 原行182–195：用直接移交队列和 AbortPolicy 建池，再交给 TTL 包装（`ThreadPoolExecutorConfig.java` L182–L195）

`new ThreadPoolExecutor(...)`（原行 182–192）的七个实参按构造器签名位置绑定。顺序写错编译器会报错，但「每个位置是什么含义」必须记住：第 1 个 `size` 是核心线程数，第 2 个 `size` 是最大线程数，`60` 与 `TimeUnit.SECONDS` 合成空闲存活时间，第 5 个 `new SynchronousQueue<>()` 是工作队列，第 6 个是线程工厂，第 7 个是拒绝策略。

核心数与最大数被写成同一个值，这一点决定了池的行为：它没有「先塞队列、再扩容到 max」的阶段。`execute` 时如果没有空闲 worker 且线程数已经到了 10，就直接进拒绝流程。`SynchronousQueue` 容量为 0，入队只有在恰好有线程等任务时才成功，所以它不缓存任何 `Runnable`；「排队」在这个池里根本不存在，真正等 15 秒的是 Redis 那边的许可队列。10 个 worker 都在跑流时，第 11 个请求在 `execute` 这一行就会失败，而不是静静排队。

原行 188–191 的线程工厂来自 Hutool 的 `cn.hutool.core.thread.ThreadFactoryBuilder`，不是 Guava 的同名类。`create()` 返回配置器，`setNamePrefix("chat_entry_executor_")` 加上 `build()` 产出一个 `ThreadFactory`，它唯一的作用是给新线程起名：排查时在 jstack 或日志里靠这个前缀认出是哪个池。它不影响池容量，也不影响拒绝策略。第 7 个实参 `AbortPolicy` 的实现是在拒绝时 `throw new RejectedExecutionException(...)`，异常在调用 `execute` 的线程上同步抛出——这正是 `ChatQueueLimiter` 能用 `catch` 接住它的机制前提。注意同一个配置类里别的池用的是 `CallerRunsPolicy`（原行 57），那里把任务回退给调用者执行；这个池故意不用，理由在「机制与工程判断」里展开。

原行 193 的 `allowCoreThreadTimeOut(true)` 打开「核心线程也允许超时退出」，配合 60 秒的存活时间，空闲线程会逐个消失。它必须在池创建之后、有任务之前调用；如果 `keepAliveTime` 小于等于 0，这里会抛 `IllegalArgumentException`。原行 194 的 `return TtlExecutors.getTtlExecutor(executor)` 返回的不是裸池，而是一个 `Executor` 包装对象：每次 `execute` 时它用 `TtlRunnable` 捕获提交线程的 TransmittableThreadLocal 快照，在 worker 线程里回放，跑完恢复。包装不改线程数、不改队列、不改拒绝策略，只负责上下文搬运；`ChatQueueLimiter` 的 `final Executor chatEntryExecutor` 字段拿到的就是这个包装。最后一行闭合方法，返回对象被 Spring 存成单例。

还有一个容易忽略的初始状态：池刚建好时线程数是 0，直接移交队列里也没有等待者。第一批请求到来时，每个提交都会发现「没有线程在等」，于是创建新 worker；前 10 个各建一个，第 11 个才会被拒。所以「池满」在冷启动时并不等于「线程都在忙」，而是「线程数已经到上限，并且每一个都在跑」。这也解释了存活时间为什么是 60 秒：请求稀疏时 worker 逐个退场，不会长期占着线程栈和内存；请求密集时它们又被复用，不必每次重建。

整组有两条看不见的事实。框架契约：注入点按类型 `Executor` 找候选，这个配置类里有 10 个 `Executor` Bean，最终能选中这一个，靠的是构造器形参名与 Bean 名一致（项目在 `pom.xml` 原行 271 打开了 `-parameters`，形参名才保留在字节码里）。底层机制：`SynchronousQueue` 是移交队列而不是缓冲区，所以「没空位」表现为一个同步异常，而不是任务悄悄堆积。

```java
    public void enqueue(String question, String conversationId, SseEmitter emitter, Runnable onAcquire) {
        if (!Boolean.TRUE.equals(rateLimitProperties.getGlobalEnabled())) {
            try {
                chatEntryExecutor.execute(onAcquire);
            } catch (RejectedExecutionException ex) {
                log.warn("直通分支线程池拒绝任务，转 reject 流程", ex);
                handleReject(question, conversationId, emitter);
            }
            return;
        }
```

##### 原行64–73：直通门：全局关闭时把工作直接交给本机执行器（`ChatQueueLimiter.java` L64–L73）

方法签名（原行 64）把「拒绝时要用的上下文」和「获准后要跑的工作」放在一起：`question`、`conversationId`、`emitter` 是拒绝分支写库和发事件所需的三个值，`onAcquire` 是 `RAGChatServiceImpl` 里那个装着整条 pipeline 的 `Runnable`。`Runnable` 只表示「有 `run()` 可调」，进入方法时它一次都没跑过；谁在哪个线程上调用 `run()`，决定了这次请求真正的执行时点。

原行 65 的 `if (!Boolean.TRUE.equals(rateLimitProperties.getGlobalEnabled()))` 有三层要读清。`getGlobalEnabled()` 返回包装类型 `Boolean`，可能是 `null`；`Boolean.TRUE.equals(null)` 是 `false`，所以「明确写 `false`」和「没配」在这里走同一条路——直通。写成 `!getGlobalEnabled()` 会先拆箱，`null` 时直接 `NullPointerException`，请求在入口就崩，而不是优雅降级。取反之后条件为真表示「全局限流没开」；配置默认是 `true`（`RAGRateLimitProperties` 原行 34），所以正常情况下这个分支不进。

`try` 里只有一句 `chatEntryExecutor.execute(onAcquire)`（原行 67）。它返回到这里只说明池「收下了」这个任务，既不保证已经开始跑，更不保证跑完；worker 线程会在之后的某个时刻调 `onAcquire.run()`。若 10 个 worker 全忙，`AbortPolicy` 在当前线程抛 `RejectedExecutionException`，同一层的 `catch`（原行 68）接住它，`log.warn("直通分支线程池拒绝任务，转 reject 流程", ex)` 留下带栈的日志，然后以三个原本就有的实参调 `handleReject`（原行 70）。注意这里没有把 `handleReject` 再 `execute` 一次：池已经满了，再提交只会再被拒一遍，拒绝消息永远发不出去；所以它在当前请求线程上同步执行。`handleReject` 内部怎么记录、发哪几个事件，由 5.3 的源码组展开。

原行 72 的 `return` 让直通分支无论成功还是拒绝都到此结束，不会继续落进下面的 `AcquireRequest` 构造；`}` 闭合 `if`。这一行是两道接收门的分岔点：走完它，本请求就已经定下了「用不用分布式许可」。

这条分支还有一个不对称之处值得记住：它没有任何等待动作。提交要么把任务交出去，要么立刻抛异常，中间没有第三种结局；所以直通模式下前端要么很快开始收到事件，要么很快收到一条拒绝，不会出现「既没开始也没拒绝」的空窗。全局限流分支恰恰相反，它有一段最长 15 秒的等待窗口，获准、超时、取消三种结局都发生在那个窗口里。

两条整组事实：语言层，拒绝异常同步抛在调用线程上，这是 `try/catch` 成立的前提，也是「直通分支的拒绝是同步拒绝」的原因；设计层，拒绝回调不在饱和的池上再排队，而是在请求线程上就地执行，用「占用请求线程一小会儿」换「拒绝消息一定有机会发出」。

```java
        chatRateLimiter.acquire(AcquireRequest.builder()
                .maxWaitMillis(TimeUnit.SECONDS.toMillis(rateLimitProperties.getGlobalMaxWaitSeconds()))
                .onAcquired(TtlRunnable.get(onAcquire))
                .onTimeout(TtlRunnable.get(() -> handleReject(question, conversationId, emitter)))
                .onAcquiredExecutor(chatEntryExecutor)
                .cancelBinder(cancel -> {
                    emitter.onCompletion(cancel);
                    emitter.onTimeout(cancel);
                    emitter.onError(e -> cancel.run());
                })
                .build());
    }
```

##### 原行75–86：分布式门：把正常回调、拒绝回调与取消绑定交给许可器（`ChatQueueLimiter.java` L75–L86）

`chatRateLimiter.acquire(...)`（原行 75）的实参是一个当场构造的 `AcquireRequest`。`AcquireRequest.builder()` 来自 Lombok 的 `@Builder`，链式调用结束时用 `build()` 生成一个 `record`；`acquire` 被注释标为「非阻塞地排队抢占一个 permit」（原行 135–137），它不会等到许可下来才返回，只负责登记和试一次。

原行 76 的 `maxWaitMillis(TimeUnit.SECONDS.toMillis(...))` 把秒换成毫秒：`TimeUnit.SECONDS.toMillis(15)` 得 `15000`。这个数字是排队预算，不是线程等待。`AcquireRequest` 的紧凑构造器会检查 `maxWaitMillis <= 0` 并抛 `IllegalArgumentException("maxWaitMillis must be > 0")`；如果配置把等待秒数写成 0，启动阶段不会报错，第一次打开全局限流的请求才会在这里炸。

原行 77 的 `.onAcquired(TtlRunnable.get(onAcquire))` 在 `enqueue` 这一行就完成了包装，这个时点很关键：`TtlRunnable.get` 在构造时捕获当前线程（也就是处理请求的 Tomcat 线程）的 ThreadLocal 快照；如果等到 limiter 的调度线程再包，捕获到的就是调度线程的上下文，`UserContext` 里的用户身份已经丢了。原行 78 的 `.onTimeout(TtlRunnable.get(() -> handleReject(question, conversationId, emitter)))` 把拒绝动作包成一个 `Runnable` 存进请求对象：箭头函数捕获三个局部变量（它们都是 effectively final，Java 要求如此），同样在这一刻捕获上下文，但不执行——只有 limiter 之后调用它时才会跑 `handleReject`。

原行 79 的 `.onAcquiredExecutor(chatEntryExecutor)` 把同一个执行器 Bean 交给 limiter，获准后由 limiter 调 `execute`，把包装好的正常回调提交进去。这就是「两个门串行」的具体含义：分布式许可成功只代表拿到了集群额度，本机池仍可能在这一步拒绝；两者不是同一个容量，也不能互相替代。

原行 80–84 的 `cancelBinder` 类型是 `Consumer<Runnable>`，作用是「把取消动作接过去」。`acquire` 建好 `Ticket` 后会调 `accept(ticket::cancel)`，于是这里的形参 `cancel` 就指向那张票据的 `cancel()` 方法。三行分别注册到 `SseEmitter` 的 `onCompletion`、`onTimeout` 和 `onError`：前两个直接接收这个 `Runnable`，`onError` 的回调接口带一个 `Throwable` 形参，lambda 用 `e` 接收却不用它，只调 `cancel.run()`。这些注册是「挂回调」，当场不执行；等 Spring MVC 的异步请求完成、超时或出错时才触发。它取消的是还在等许可的那张票据，不是正在跑的模型调用。最后 `.build()` 把等待值、两个 `Runnable`、执行器和取消绑定组装成 `AcquireRequest`，交给 `acquire` 消费。

原行 86 的 `}` 闭合方法。到这里，本单元能确认的最后一件事是：`enqueue` 返回时，全局分支的请求只是「登记完毕」，真正跑没跑、什么时候跑，取决于 limiter 内部的票据状态机。

请求对象是一个记录类型，字段依次是等待毫秒数、正常回调、拒绝回调、执行器和取消绑定。构建器的方法名与字段同名，所以这几行链式调用的书写顺序其实不影响结果——真正决定行为的是构建结束时那个对象的字段值。这一点和执行器构造器不同：那里靠位置，错位就换含义；这里靠名字，顺序只影响可读性。两种绑定方式混在一起读，很容易误以为调换链式顺序会改变语义。

还有一处时序要盯住：三行取消注册必须在进入许可器之前完成，因为许可器需要拿到这个消费者，才能把票据自己的取消方法接进去。如果注册晚于这次调用，取消动作就没有接收者，用户点停止时票据仍然留在队列里，直到等满 15 秒才超时——前端看起来就是「点了没反应」，而后端日志里只有一次平平无奇的超时。

整组两条看不见的事实。框架契约：`AcquireRequest` 的紧凑构造器对 `onAcquired`、`onTimeout`、`onAcquiredExecutor` 做 `Objects.requireNonNull`，少传一个不会在编译期报错，会在调用处抛 `NullPointerException`。底层机制：TTL 快照必须在请求线程捕获，晚一步就换了线程身份；`Runnable` 的包装位置决定了它携带哪一份上下文。

```java
    private static final String CHAT_LIMITER_NAME = "rag:global:chat";

    @Bean(initMethod = "start", destroyMethod = "stop")
    public FairDistributedRateLimiter chatRateLimiter(RedissonClient redissonClient,
                                                      RAGRateLimitProperties rateLimitProperties) {
        return new FairDistributedRateLimiter(
                CHAT_LIMITER_NAME,
                redissonClient,
                rateLimitProperties::getGlobalMaxConcurrent,
                rateLimitProperties::getGlobalLeaseSeconds,
                rateLimitProperties::getGlobalPollIntervalMs
        );
    }
```

##### 原行31–43：限流器 Bean：initMethod 把容器启动接到 start()（`ChatRateLimiterConfig.java` L31–L43）

原行 31 的 `CHAT_LIMITER_NAME = "rag:global:chat"` 是 Redis 侧的共享资源名。它是 `static final`，在编译期就固定成这个字符串；集群里每个实例都必须用同一个名字，才会看到同一个信号量和同一条队列。改这个常量等价于换一套资源：老队列里还在等的请求，新实例完全看不见。

原行 33 的 `@Bean(initMethod = "start", destroyMethod = "stop")` 是生命周期接线，不是普通方法调用。Spring 在完成这个 Bean 的实例化和依赖注入之后，按名字调用它的 `start()`；容器关闭时调用 `stop()`。两个名字都是字符串，拼错不会编译报错，只会在启动创建 Bean 时失败。没有这一行，`start()` 永远没人调，`trySetPermits` 不会执行、通知监听也不会注册——「Spring 启动时调用 start()」这句话的全部依据就在这里；`start()` 内部到底写了什么，由下一个单元（5.2.2）的源码组读。

原行 34–35 的两个形参由 Spring 注入：`RedissonClient` 是 Redisson 的客户端 Bean，`RAGRateLimitProperties` 是前面那个配置类。返回类型写成具体的 `FairDistributedRateLimiter` 而不是接口，是因为 `initMethod`/`destroyMethod` 要在这个类型上按名字找方法，接口上没有 `start`/`stop` 就找不到。

原行 36–42 的 `new FairDistributedRateLimiter(...)` 五个实参按构造器位置绑定：资源名、Redisson 客户端，然后是三个方法引用 `rateLimitProperties::getGlobalMaxConcurrent`、`::getGlobalLeaseSeconds`、`::getGlobalPollIntervalMs`。方法引用在传参这一刻只做「绑定对象 + 方法」，不调用 getter；它们被适配成 `IntSupplier`，等 limiter 真正需要时才 `getAsInt()`。这就是为什么这里不写成「先取三个 int 再传」：取早了就把值冻在装配期，`start()` 里的 `trySetPermits` 和后续运行期读到的都会是旧值。最后一行闭合方法，返回值被容器注册成名为 `chatRateLimiter` 的单例，`ChatQueueLimiter` 的 `final FairDistributedRateLimiter chatRateLimiter` 字段拿到的就是它。

还有一个容易被忽略的后果：Bean 名和两个回调方法名都是字符串，重构时把方法改了名却不同步注解，编译照样通过，容器却起不来；反过来，注解里的名字写成不存在的方法，报错也发生在创建这个单例的时候，而不是第一次请求。排查这类问题要看启动日志里这个 Bean 有没有创建成功，而不是等用户报错。它同时也说明一件事：这个对象的启动时机完全由容器决定，代码里没有任何一处显式调用，所以「服务已经能处理请求」和「限流器已经启动」之间没有时序竞争——容器不会把半初始化的 Bean 交给请求。

两条整组事实。框架契约：`initMethod`/`destroyMethod` 是 Spring `@Bean` 的标准生命周期回调，走反射按名字找方法，与接口无关；Bean 的创建时点早于任何请求。设计层：传 supplier 而不是传值，把「什么时候读配置」从装配期推迟到使用期，代价是每次读都多一次方法调用。

```java
    public FairDistributedRateLimiter(String name,
                                      RedissonClient redissonClient,
                                      IntSupplier maxPermitsSupplier,
                                      IntSupplier leaseSecondsSupplier,
                                      IntSupplier pollIntervalMsSupplier) {
        this.name = Objects.requireNonNull(name);
        this.redissonClient = Objects.requireNonNull(redissonClient);
        this.maxPermitsSupplier = Objects.requireNonNull(maxPermitsSupplier);
        this.leaseSecondsSupplier = Objects.requireNonNull(leaseSecondsSupplier);
        this.pollIntervalMsSupplier = Objects.requireNonNull(pollIntervalMsSupplier);
```

##### 原行81–90：构造器按位置接住配置 supplier，并逐个拒绝 null（`FairDistributedRateLimiter.java` L81–L90）

构造器签名（原行 81–85）的五个形参类型分别是 `String`、`RedissonClient` 和三个 `IntSupplier`，正好对应配置 Bean 传进来的五个实参位置。`IntSupplier` 是 JDK 的函数接口（无参、返回 `int`），方法引用的目标方法签名必须能适配它；`getGlobalMaxConcurrent` 返回 `Integer`，适配时会自动拆箱成 `int`——所以如果配置字段是 null，getter 一被调用就 NPE，而它第一次被调用是在 `start()` 里。

原行 86–90 的五条 `Objects.requireNonNull(...)` 一边校验一边赋值。`requireNonNull(x)` 的返回值就是 `x` 本身，所以 `this.field = Objects.requireNonNull(arg)` 同时完成「检查非空」和「保存引用」；遇到 null 立刻抛 `NullPointerException`，后面的键派生、Lua 加载、调度器创建一条都不会执行。存进去的是同一个引用、同一个字符串对象，不是副本。

为什么不依赖后面自然发生的 NPE：早失败能指名是哪个依赖为空，晚失败会拖到 Redis 调用或线程命名时才炸，栈更深、更难定位。构造器的失败形态也值得记住：如果这里抛了，Spring 创建 `chatRateLimiter` Bean 失败，容器启动直接中止——这个 Bean 是单例，并且被 `ChatQueueLimiter` 依赖。不会出现「服务起来了但限流器是半成品」的状态；这与请求期失败是两种完全不同的故障，前者启动即暴露。

顺带说清一个容易混淆的点：这里的非空检查发生在装配阶段，而不是请求阶段。如果 Redisson 客户端注入失败，或者配置对象本身不存在，错误会以「容器启动失败」的形式出现，而不是等到第一个用户请求才炸；反过来说，这些字段在运行期不可能变成 null，后面的代码也就不需要反复判空。把假设钉死在最靠近来源的地方，比在每个使用点各防御一次更省心，也更容易在启动日志里一次看清缺了什么。

两条整组事实。语言层：方法引用在字段赋值时只解析方法、不调用 getter，`requireNonNull` 返回入参，因此可以链在赋值右侧。框架契约：构造器通过之后 Spring 还会执行 `initMethod`，构造器只负责造出一个「可用但未启动」的对象。

```java
        this.semaphoreKey = name + ":semaphore";
        this.queueKey = name + ":queue";
        this.queueSeqKey = name + ":queue:seq";
        this.notifyTopicKey = name + ":queue:notify";
        this.entryKeyPrefix = name + ":entry:";
        this.claimLua = loadLuaScript();
```

##### 原行92–97：由同一个资源名派生 Redis 键，并在构造期载入 Lua（`FairDistributedRateLimiter.java` L92–L97）

原行 92–96 的五个实例字段全部由 `name` 派生：`name + ":semaphore"`、`":queue"`、`":queue:seq"`、`":queue:notify"`、`":entry:"`。代入 `name = "rag:global:chat"`，得到 `rag:global:chat:semaphore`、`rag:global:chat:queue`、`rag:global:chat:queue:seq`、`rag:global:chat:queue:notify`，以及前缀 `rag:global:chat:entry:`。这些字符串是每个实例访问的 Redis 键，也是实例之间唯一的共享契约：键名不一致，两个实例就各自维护一套队列，公平性直接失效。`entry:` 后面还要拼 `requestId`，所以它是前缀而不是完整键。

原行 97 的 `loadLuaScript()` 在构造期间读 classpath 上的 `lua/queue_claim_atomic.lua`（常量在 57 行），用 `StreamUtils.copyToString(..., StandardCharsets.UTF_8)` 变成 `String` 存进 `claimLua`；读不到会包成 `IllegalStateException("加载 Lua 脚本失败：" + LUA_PATH, ex)`。这里只加载脚本文本，不碰 Redis、不执行脚本；脚本被谁在什么时机 `eval`，是下一个单元的内容。代价是改脚本必须重启，收益是每次抢占不用读文件。第 91 行是空行，不属于引用范围，它只是把「字段赋值」和「资源键派生」两段隔开。

这里有个容易低估的风险：五个键只有前缀来自同一个字符串，后缀是手写的字面量。如果哪天有人把某一个后缀改成复数、或者多加一个冒号，编译器和单元测试都不会报错（键名只是普通字符串，不经过任何框架校验），运行时的表现却是「信号量和队列对不上」——许可被某一边拿走，队列另一边没人消费。所以这类键名在项目里通常集中在一处生成，本文件的构造函数就是这么做的；改动它之前要先确认没有别处硬编码了同样的字符串。

加载脚本那一步也值得把失败形态记住：文件不在 classpath 里、编码读错、流没关，最终都会变成同一个启动异常，消息里带着脚本路径。它不会退化成「没有脚本也能跑」，因为后面的抢占逻辑离不开这段文本；把失败提前到启动期，是为了避免第一条真实请求才暴露问题，也避免一个实例带着空脚本进入集群。

两条整组事实。底层机制：键名是跨进程契约，分布式共享状态全靠字符串对齐，拼错不会有任何编译或运行错误，只会表现为「队列不生效」。设计层：构造期加载脚本，用「启动失败」换「运行期零 I/O」。

```java
        String threadPrefix = name.replace(':', '_');
        int schedulerSize = Math.min(4, Math.max(2, Runtime.getRuntime().availableProcessors() / 2));
        AtomicInteger threadCounter = new AtomicInteger();
        this.scheduler = new ScheduledThreadPoolExecutor(schedulerSize, r -> {
            Thread t = new Thread(r);
            t.setName(threadPrefix + "_scheduler_" + threadCounter.incrementAndGet());
            t.setDaemon(true);
            return t;
        });
```

##### 原行99–107：调度器按 CPU 数定容、守护线程命名（`FairDistributedRateLimiter.java` L99–L107）

原行 99 的 `name.replace(':', '_')` 把 `rag:global:chat` 变成 `rag_global_chat`。冒号在 Redis 键名里是层级分隔符，在线程名里却不便于按前缀过滤和日志检索，所以这里换掉。生成的是局部变量，只用于线程命名。

原行 100 的 `Math.min(4, Math.max(2, Runtime.getRuntime().availableProcessors() / 2))` 是三层嵌套：先 `availableProcessors() / 2` 用整数除法向下取整，再 `Math.max(2, ...)` 把小结果抬到 2，最后 `Math.min(4, ...)` 把大结果压到 4。8 核机器得 4，4 核得 2，1 核或 2 核也被抬到 2。`availableProcessors()` 按 JVM 当时可见的 CPU 数返回，所以这个值在构造这一刻求值一次，之后不再变。

原行 101 的 `new AtomicInteger()` 从 0 开始，专门给线程工厂编号。之所以用原子类型，是因为线程工厂可能在多个线程里被并发调用（池同时创建多个 worker 时），普通 `++` 会重复。原行 102–107 的 `new ScheduledThreadPoolExecutor(schedulerSize, r -> {...})` 第二个实参是一个 `ThreadFactory`：`r` 是池交进来的任务。这个 lambda 现在不执行，只是把「需要一个新线程时怎么造」的规则交给池。池第一次要执行定时任务时调用它：`new Thread(r)` 把该任务设成新线程的目标，`setName(threadPrefix + "_scheduler_" + threadCounter.incrementAndGet())` 命名并递增编号，`setDaemon(true)` 设为守护线程，`return t` 交回池。

原行 108–109 不在本组范围内，但要先说清它们的去向：第 108 行把刚建好的调度器交给 `PollNotifier`，第 109 行闭合构造器。这两行是 5.2.2 的第一组，那里会把 `new PollNotifier(this::availablePermits, scheduler)` 贴出来逐行讲——这里只交代本单元必须知道的一点：构造器结束时，调度器已经有了第二个使用者，它不再只跑定时任务，也会在跨实例通知到达时被拿来执行扫描。所以本单元谈的「构造期把对象装好」到这个位置才算闭合，池的容量与线程名规则在下一单元仍然有效。

为什么调度器要有上限。每个 limiter 实例都会长期持有这个池，如果按核数无上限地开，一台 64 核的机器会为一个组件留下三十多个定时线程；反过来只给两个，扫描任务排队又会拖慢许可的及时发放。取「核数一半、夹在 2 到 4 之间」是个折中：小机器不至于只有一根线程，大机器也不会被同一个组件吃掉太多资源。守护属性再补上一层保险——即使某次停机路径没走到关闭方法，这些线程也不会把 JVM 拖住不退出。

命名规则也服务于排查：前缀来自资源名，后缀是序号，所以一个进程里存在多个 limiter（比如不同业务各有一个）时，线程名能直接告诉你是哪一个在跑。定时任务出错时日志里往往只有线程名，这一点比匿名线程重要得多。

两条整组事实。底层机制：守护线程不阻止 JVM 退出，但它们仍必须在 `stop()` 里 `shutdown`，否则任务和队列不会被释放，且 `stop()` 还负责等它终止。设计层：复用调度器而不是给 notifier 单开线程池，避免每个 limiter 实例多出一组常驻线程。

#### 同输入局部运行与实际重要失败

先把同一组值代进直通分支：`enabled=false`、池大小 10、10 个 worker 都在跑上一条流。`enqueue` 在 `if` 处取反后为真，进入直通，`execute(onAcquire)` 找不到空闲 worker，`AbortPolicy` 当场抛 `RejectedExecutionException`；`catch` 在同一层接住，日志 `直通分支线程池拒绝任务，转 reject 流程` 带上异常栈，`handleReject(请总结这份文档, C-100, emitter)` 在**当前请求线程**上执行。如果 `handleReject` 里的两次 append 都成功，前端会依次收到 META、REJECT、FINISH、DONE（5.3 逐行读）；`enqueue` 的 `return` 保证它不会再去碰 limiter。残留状态是：池里那 10 条流继续跑，本次请求没占用任何 worker，也没拿许可。

再把开关换回默认的 `true`：`if` 为假，构造 `AcquireRequest`，`maxWaitMillis=15000`，两个回调都包好，交给 `acquire`。`acquire` 登记完就返回，`enqueue` 随即返回，Controller 把 emitter 交回 Spring MVC，连接挂住等事件。此后分两条：15 秒内拿到许可，limiter 把 `onAcquired` 提交给 `chatEntryExecutor`，池有空位才真正开始 `chatPipeline.execute`；15 秒到点没拿到，`Ticket.timeout` 把 `onTimeout` 提交给同一个执行器。关键失败就在这里：如果 10 个 worker 仍然全忙，这次提交抛 `RejectedExecutionException`，被 `submitSafely` 捕获后只留一条 `onTimeout 提交失败，回调被丢弃` 的 warn，`handleReject` 一次都没跑。前端收不到任何拒绝事件，要等 emitter 自己的超时被 Spring MVC 触发，用户才看到连接断开或报错——这就是「请求被拒绝」与「拒绝消息落库」可能脱节的地方。

第三种失败来自配置而不是流量：把 `max-wait-seconds` 配成 0，`TimeUnit.SECONDS.toMillis(0)` 得 0，`AcquireRequest` 的紧凑构造器抛 `IllegalArgumentException("maxWaitMillis must be > 0")`。异常从 `enqueue` 抛到 `streamChat`，再抛到 Controller；emitter 已经创建但一个事件都没发，Spring MVC 走错误处理，前端看到请求失败而不是一条「系统繁忙」。这类失败属于装配错误，不属于限流拒绝。

第四种失败更隐蔽：假设有人把 `.onTimeout(...)` 外面的 `TtlRunnable.get` 去掉。`onTimeout` 由 limiter 的线程执行时，`TransmittableThreadLocal` 里没有请求线程写入的 `UserContext`，`handleReject` 取不到 `userId`，记录那一步会退化成「只发 DONE、不落两条消息」——同一段代码在直通分支看起来正常（它在请求线程上跑），一开全局限流就变形。这个对比说明 TTL 包装不是装饰，而是这条链上最脆弱的一处接线。

#### 机制与工程判断

为什么必须是两道门。本机池回答的是「这台机器现在有没有 worker 能跑」，分布式许可回答的是「整个集群现在允不允许再跑一条」。两个问题分别由不同的资源回答，所以只能串行、只能都过。合并成一道会丢掉一个维度：只留本机池，N 台机器就是 N 份并发，供应商侧的配额和成本随扩缩容漂移；只留分布式许可，一台机器可能被分到超过它线程数的许可，许可被占着却没人跑，集群吞吐反而下降。

为什么这里用 `SynchronousQueue` 加 `AbortPolicy`。等待能力已经由分布式队列提供（15 秒预算、按 score 排队），本机池再缓存一层排队只会制造第二个排队系统：任务在池队列里等，许可却已经被它拿着，等待时间不进 `maxWaitMillis` 的账，超时语义就失效了。直接用移交队列加拒绝策略，让「本机没空」立刻变成一个同步可捕获的事件，由调用方决定怎么体面地拒绝。换成 `CallerRunsPolicy` 的代价很具体：`enqueue` 是在 Controller 返回 emitter 之前被调用的，任务一旦回退到当前线程执行，整条流跑完之前响应头都发不出去，SSE 变成「等几十秒再一次性回放」，而且 Tomcat 的请求线程被占住。换成 `LinkedBlockingQueue(200)`（配置类里别的池就是这么写的）则会让本机也排起队，许可被长时间占住，`maxWaitMillis` 失去意义。

为什么核心数等于最大数、还允许核心超时。这个池的职责只是「给获批的流一个 worker」，不需要预热，也不需要「先扩容到 max」的弹性。两个数相等，语义最简单：同时最多 10 条流。`allowCoreThreadTimeOut(true)` 加 60 秒让空闲线程归还，代价是突发时每个新线程要创建（微秒级），相对一次几秒到几十秒的模型流可以忽略；收益是空闲实例不长期占着 10 个线程栈和对应的内存。

为什么 TTL 要包两层。`chatEntryExecutor` 已经是 `TtlExecutors` 包装的 `Executor`，`onAcquired`/`onTimeout` 却还要显式 `TtlRunnable.get`，因为「捕获」发生在包装对象构造的那一刻，而不是执行的那一刻。这两个回调会在 limiter 的调度线程或通知线程上被提交，如果等到那时才捕获，拿到的是 limiter 线程的上下文；在 `enqueue` 里包，捕获的才是请求线程的 `UserContext`。外层再包一次不会改变结果：外层回放的是提交线程的快照，内层回放的是请求线程的快照，真正的任务看到的是内层——也就是我们要的那份。

十倍并发先坏在哪。池和许可都放大十倍（100）时，先到上限的不是这个池，而是 Tomcat 的连接数、每条 SSE 流占的堆缓冲、以及模型供应商的 QPS 与配额。池这时是「对齐器」而不是瓶颈：它保证本机同时在跑的流不超过许可数。反过来的错配更危险：许可 100、池 10，拿到许可的 90 个请求会卡在 `execute` 被拒、释放许可、走 `onTimeout`、再被拒，日志里连续出现两种 warn，表现为「明明还有额度却大量拒绝」。所以 `chatEntryExecutor` 的大小读的是同一个 `getGlobalMaxConcurrent`，这不是省事，而是刻意的对齐。

还有一个容易忽略的边界：许可和线程不是同一个生命周期。许可在业务跑完的 finally 里释放，而线程在任务结束后回到池里等下一个任务；业务代码抛出的未捕获异常会先经过这个 finally，于是许可照样释放、线程也照样活着回到池里，只是这条流的事件链断了。反过来，如果持许可的线程被长时间阻塞（比如模型接口迟迟不返回首字），池里的名额和 Redis 里的许可会同时被占满，此时新请求在分布式门就开始排队，而不是等到本机门——这正是两道门顺序带来的可观测差异：先满的那一道，决定了拒绝发生在哪里、日志里出现哪一条 warn。

一个可行的替代方案：给拒绝回调单独一条执行通道（比如 `chatRejectExecutor`，小池加 `CallerRunsPolicy`），让拒绝不受业务池饱和影响。代价是多一组常驻线程，且拒绝风暴时它自己也需要限流；收益是「拒绝消息一定送达」从「碰运气」变成结构性保证。本单元没有实施这个改动，只在下一节给出接线清单。

#### 怎么用、上下游、接入与修改影响

假设真要把上面那条替代方案做出来，接线点是四个，漏一个就白改。第一，在 `ThreadPoolExecutorConfig` 里新增 `@Bean public Executor chatRejectExecutor()`，方法名必须与注入点字段名一致。第二，在 `ChatQueueLimiter` 加 `private final Executor chatRejectExecutor;`，`@RequiredArgsConstructor` 会把它变成构造器参数，参数名即字段名。这里是本项目最容易踩的坑：同一个配置类里有 10 个 `Executor` Bean，Spring 按类型找到 10 个候选，最后靠参数名匹配；项目在 `pom.xml` 原行 271 打开了 `-parameters`，形参名才保留在字节码里。字段改名而不同步 Bean 名，启动直接 `NoUniqueBeanDefinitionException`。

第三，`AcquireRequest` 现在只有一个 `onAcquiredExecutor`，`Ticket.grant`（227 行）和 `submitSafely`（292 行）都用它提交；要让 `onTimeout` 走新池，得给 record 增加一个字段、或让 `submitSafely` 接收执行器，并同步 `builder()` 的调用点。漏改 `submitSafely` 的话新池根本不会被用到，日志看起来一切正常，拒绝仍然丢。第四，`cancelBinder` 那边不用动，但要在测试里确认取消仍然只作用于等许可的票据。

另一个更常见的改动是调并发数：只改 `application.yaml` 的 `max-concurrent`（原行 106），就会同时改池大小（原行 181 读同一个 getter）和 `start()` 里的 `trySetPermits`，这是有意的「一个数字对齐两道门」。如果只在代码里把池写死成 20 而许可仍是 10，多出来的 10 个线程永远拿不到工作；反过来则会出现「有许可没线程」的拒绝。

排查入口有三处：启动日志里 `chatEntryExecutor` 与 `chatRateLimiter` 是否成功创建（Bean 名、`initMethod` 拼写）；线程名里有没有 `chat_entry_executor_` 前缀（确认是哪个池在跑）；两条 warn 的原文——`直通分支线程池拒绝任务` 说明全局开关是关的、拒绝走同步路径，`onTimeout 提交失败` 说明全局分支的拒绝回调被池挡掉了。再往下就进入 5.2.2：`acquire` 如何建票据、如何入队、如何超时。

### 5.7.2 气泡内部：一条消息怎么变成气泡，Markdown、代码块与四个入口各自接在哪

#### 实际问题与实现思路

5.7.1 把 `Message` 对象送到了 `MessageItem` 的 `props` 上，但送到的只是一个对象；用户看到的是一个气泡：用户消息是纯文本段落，助手消息是 Markdown 正文，可能有思考面板、代码块、引用角标，底部还有复制、点赞点踩、来源、推荐追问几个入口。本单元读的就是同一条 `Message` 在这一个组件里被拆成哪几种形态，以及每一块内容由什么条件决定显不显示。

需要回答四个问题。第一是**角色分支**：为什么用户消息走一条单独的 `return`，而不是和助手共用 Markdown 渲染。第二是**内容分派**：`content`、`thinking`、`sources`、`status` 四个字段分别喂给哪些子组件，哪些是「有值才渲染」、哪些是「状态到了才渲染」。第三是**入口接线**：复制、反馈、来源、推荐追问这四个按钮各自把值送进哪个 Store action，为什么气泡本身不直接发请求。第四是**未完成处理**：流式过程中这条消息还只是半截文本，渲染层靠什么避免「半个代码块」「点不动的角标」「给半截回答点赞」这类问题。

还有一个必须点破的边界：本项目的消息气泡里**没有「重新生成」**。全前端搜 `regenerate` 没有命中，唯一的「停止生成」在输入框里（`ChatInput.tsx:126–127`，按钮图标从 `Send` 换成 `Square`），而气泡里的四个入口是复制、点赞点踩、来源、推荐追问。这不是漏写，而是这个产品的取舍：重新生成需要「重发上一条用户消息并复用同一条助手行」，会动到「一问一答」的不变式，本单元最后一节会讲要接的话得改哪里。

#### 架构位置、真实触发与输入准备

调用链：`MessageList` 的 `itemContent`（5.7.1）把数组元素交给 `MessageItem` → `MessageItem` 按 `role` 分两条路 → 助手走 Markdown 分支，把 `content`/`messageId`/`sources` 传给 `MarkdownRenderer` → `MarkdownRenderer` 把 Markdown 字符串交给 `ReactMarkdown`，用 `remark` 插件解析、用 `components` 覆盖代码块与链接 → 代码块再嵌一个 `CopyButton`。控件方向相反：气泡只负责「什么时候显示」，点击后调的是 Store 里的 action（`submitFeedback`、`toggleSourcesPanel`、`sendMessage`、`loadRecommended`）。

真实触发沿用同一组输入：`assistant-LOCAL-1` 正在流式，`content` 从 `"你"` 涨到 `"你好"`，`status="streaming"`；同一时刻另有一条已完成的用户消息 `user-1`、一条已完成的助手消息 `M-301`（带 `sources` 与 `feedback=null`）、一条被拒绝的助手消息 `M-300`（`messageStatus="REJECTED"`）。为了读代码块路径，再把 `content` 换成一段真实回答：普通段落、一个围栏代码块、一个行内代码、一个引用角标 `[1]`。

版本与上一个单元一致：react 18.3.1、react-markdown 声明 `^9.0.1` 实际装 9.1.0、react-syntax-highlighter（Prism 版）。9.1.0 的依赖里有 `remark-parse ^11`、`remark-rehype ^11`、`mdast-util-to-hast ^13`，所以「Markdown 字符串 → mdast → hast → React 元素」这条管线是库内固定动作，不是本项目自己写的解析器。

#### 源码定位与阅读准备

本单元读两个文件。`frontend/src/components/chat/MessageItem.tsx`：用户分支 41–49 行、助手分支的耗时标签与思考指示器 51–57 行（58–91 行的可折叠思考面板在正文里讲，不再单独引用）、内容区 92–111 行、控制器 112–121 行（122–128 行的来源与推荐按钮在正文里讲）。`frontend/src/components/chat/MarkdownRenderer.tsx`：入口与插件配置 174–188 行、代码组件的判定 189–197 行、代码块分支的表头 212–218 行。另外两处只在正文里引：`FeedbackButtons.tsx:103–114` 的消息级复制、`ChatInput.tsx:126–127` 的停止生成。仓库 revision `16984b95454d3fc2a55b60ade1950fefeba339ec`。

读之前补四个前置。第一，`MessageItem` 是一个 `React.memo` 函数组件（5.7.1），组件体里 `message.status`、`message.content` 这类字段都是本次快照的值，没有第二份状态；唯一的本地状态是 `useState(false)` 的思考面板展开开关（36 行）。第二，JSX 里的 `{condition ? <X/> : null}` 是普通三元表达式，条件为假时该子元素根本不创建，不是「隐藏」。第三，`trim()` 只用来判断「有没有可见字符」，判断完传给下游的仍是原始字符串——空白在 Markdown 里有语义（缩进代码块、表格对齐），不能用裁剪后的值。第四，`status` 的类型是 `"streaming" | "done" | "cancelled" | "error"`（`frontend/src/types/index.ts:5`），`messageStatus` 是另一套「落库状态」`"NORMAL" | "INTERRUPTED" | "REJECTED"`（`:7`），两者不是一个东西：前者描述前端此刻的渲染态，后者描述后端存下来的业务结果。

#### 4–5 连续源码与紧邻逐行推导

```tsx
  if (isUser) {
    return (
      <div className="flex">
        <div className="user-message">
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      </div>
    );
  }
```

##### 原行41–49：用户角色提前返回：纯文本段落，不做 Markdown（`MessageItem.tsx` L41–L49）
这一组是整份代码里最短也最关键的一条分支。`if (isUser)` 里的 `isUser` 来自 18 行的严格比较；条件成立就 `return` 一棵只有两层的 `div` 加一个 `p`，组件函数在这里结束，后面所有助手专用的分支（思考指示器、思考面板、Markdown、反馈、来源、推荐）都不会执行。

`{message.content}` 作为 `<p>` 的子节点插进去，得到的是一个**文本节点**，不是 HTML。React 在创建文本节点时会把 `&`、`<` 这类字符转义，所以用户打出 `<img src=x onerror=alert(1)>`，页面上显示的就是这串字符本身，不会生成 `<img>` 元素。这一点值得单独记住：不是这段代码做了什么防护，而是 JSX 的文本子节点本来就只接受字符串，绕过它必须用 `dangerouslySetInnerHTML`，而这里没有用。

两个类名各有作用。`whitespace-pre-wrap` 对应 CSS 的 `white-space: pre-wrap`：保留换行与连续空格，同时在超宽时自动折行。用户消息是多行输入框写出来的，换行是用户的本意，如果按浏览器默认的 `normal` 处理，所有换行会被压成一个空格，多行提问会挤成一整段。`break-words` 对应 `overflow-wrap: break-word`：当一段没有空格的超长串（比如一长串 URL、一段没断点的十六进制）出现时，允许从任意位置断开，否则会撑破气泡、产生横向滚动条。

实际触发什么？`user-1` 这条消息进入组件后，React 创建一个 `div.flex`、一个 `div.user-message`、一个 `p`，把 `content` 作为文本子节点。全程不解析 Markdown、不高亮代码、不查引用，也不读 `message.status`——用户消息没有流式过程，它的 `status` 恒为 `done`。所以这段路径的成本与内容长度近似线性，一个几千字的提问也不会卡。

不这样写会怎样？把用户消息也送进 `MarkdownRenderer`，功能上「用户也能用 Markdown」听起来更好，代价有三：一是用户文本的信任级别更低，而 `MarkdownRenderer` 打开了 `rehypeRaw`（189 行），虽然紧跟了 `rehypeSanitize`，但把攻击面从「纯文本」扩到了「过滤后的 HTML」；二是用户提问往往含大量 `*`、`_`、`#`、`[]`，会被误解析成列表、标题、链接，显示出来和用户输入的完全不一样；三是每条用户消息都要走一遍解析管线，长会话里这是纯浪费。

这一组两条整组事实。框架契约：JSX 的字符串子节点按文本处理，字符实体由 React 转义；要有富文本必须是元素或者显式开启的原始 HTML 通道。底层与设计：用户与助手分成两条渲染路径，本质是**信任与需求不同**——用户文本只需原样、可换行地展示；助手文本是模型生成的结构化内容，必须解析成可读的排版。

```tsx
        <div className="space-y-2">
          {isWaiting ? (
            <div className="ai-wait" aria-label="思考中">
              <span className="ai-wait-dots" aria-hidden="true">
                <span className="ai-wait-dot" />
                <span className="ai-wait-dot" />
                <span className="ai-wait-dot" />
              </span>
            </div>
          ) : null}
```

##### 原行92–101：等待态：三个点只在「流式中、非思考、无正文」时出现（`MessageItem.tsx` L92–L101）
这一组处理「消息刚建出来、还没有字」的那一小段时间。外层 `<div className="space-y-2">` 是内容区的容器，`space-y-2` 给区内的各个子块统一加竖直间距；里面第一个条件就是 `isWaiting`（39 行：`status === "streaming" && !isThinking && !hasContent`），为真时渲染一个 `div.ai-wait`，里面一层 `span.ai-wait-dots` 包着三枚 `span.ai-wait-dot`。

三个 `aria` 属性各管一件事。`aria-label="思考中"` 给这个没有文字的容器一个可读名字，屏幕阅读器会把「思考中」念出来；`aria-hidden="true"` 标在点列上，把三枚纯装饰的点从无障碍树里摘掉，否则它们会被当成无意义的空内容；三枚 `span` 本身没有文字，动画完全由 CSS 类承担（`ai-wait-dots`/`ai-wait-dot` 的样式在全局样式里），React 这边不做任何计时或轮播。

为什么用「派生条件」而不是一个 `isWaiting` 状态字段？因为等待态完全可以从已有数据算出来：只要还在流式、没有思考内容、正文为空，它就是等待态。多存一个布尔就要在每条路径上同步它——收到第一个 delta 时要关、收到 think 时要关、报错时要关、取消时要关——漏一处就会出现「已经有字了三个点还在转」或者「报错了还在转」的错位。派生值没有这个问题，代价是每次 render 多算三个判断，可以忽略。

实际触发什么？占位助手刚被创建时，`content=""`、`status="streaming"`、`isThinking=false`，三个条件同时成立，点列出现。第一个 `MESSAGE` 到达后 `content="你"`，`hasContent`（`trim().length > 0`）为真，条件变假，整棵子树被卸载，同一帧里 `MarkdownRenderer` 那条分支变真——视觉上是「点消失、字出现」，实现上是一次条件切换，不是两个组件互相淡入淡出。

不这样写会怎样？如果把三点的显示条件写成 `content === ""`，那么一条被取消、`status="cancelled"` 的空消息会永远转圈；如果写成「只要 streaming 就显示」，它会在思考、作答全程一直转，看起来像卡死。若把等待态做成独立状态字段，最容易出的 bug 是「后台事件顺序异常时字段没被重置」，表现就是永远转圈、刷新才好。

这一组两条整组事实。框架契约：JSX 里 `null` 表示「这个位置上没有子元素」，对应组件会被卸载、`useEffect` 清理函数会执行；它不是 `display: none`，不占位、不参与布局。底层与设计：把「是否等待」做成派生值，是 React 里最省心的状态设计——状态的唯一来源是数据本身，不需要额外的同步协议。

```tsx
          {hasContent ? (
            <MarkdownRenderer
              content={message.content}
              messageId={message.id}
              sources={message.sources}
            />
          ) : null}
          {message.status === "error" ? (
            <p className="text-xs text-rose-500">生成已中断。</p>
          ) : null}
```

##### 原行102–111：正文与错误：有可见字符才交给 Markdown 渲染器，error 另起一行提示（`MessageItem.tsx` L102–L111）
这一组是「文本 → 气泡主体」的正式交接。`hasContent`（38 行，`message.content.trim().length > 0`）为真时创建 `MarkdownRenderer`，三个 prop 分别是完整 `content`、当前 `message.id`、`message.sources`。注意传的是**整条累积正文**，不是本次 delta：Store 里 `content` 已经拼好了全文（5.7.1），渲染层拿到的永远是「从头到现在」的完整字符串，Markdown 语法（列表、代码围栏、表格）因此每一帧都是完整的、可以重新解析。

`messageId={message.id}` 在 `MarkdownRenderer` 里有两个用途：解析正文里的 `[N](#cite-N)` 角标时把它交给 `SourceCitation`（`MarkdownRenderer.tsx:264–275`），以及让来源面板知道「这是哪条消息的来源」。流式期间它是临时 id（`assistant-…`），FINISH 之后才换成真实 `M-301`——这个替换对渲染没有影响，但对「点角标打开来源面板」有影响，因为面板是按 messageId 查的。

第三个 prop `sources={message.sources}` 在流式期间通常是 `undefined`：来源列表随 FINISH 的 `CompletionPayload` 一起到（5.6）。这就是为什么 `sources` 在类型上是可选的（`types/index.ts:46`），也是为什么渲染层必须能处理「正文里已经有 `[1]`、但 `sources` 还没到」的中间态。

`hasContent` 用 `trim()` 判断，但传下去的是原字符串。这个不对称是刻意的：模型有时会先输出几个换行或空格，如果按原字符串判空，会出现「正文区已经存在但看起来什么都没有」的空窗；而传原字符串保证 Markdown 解析看到的是作者原本的缩进和空行——把 `trim()` 的结果传下去，依赖缩进的代码块会立刻失效。

第二个条件是 `message.status === "error"`，为真时额外渲染一行红字「生成已中断。」。它和上一个条件是并列的，不是二选一：一条已经收到几百字、随后流断掉的消息，会同时显示 Markdown 正文和这句提示——这正是想要的，用户既看得到已有内容，也知道它不完整。

这一组两条整组事实。框架契约：`MarkdownRenderer` 没有被 `React.memo` 包住，父组件每次重渲染它都重新执行，`content` 变了就重新解析全文；这是有意的，因为流式正文每一帧都不同。底层与设计：「判断用裁剪值、传值用原值」是文本渲染里少见的、必须保留的不对称；把它统一成任一种都会引入一类难查的显示 bug。

```tsx
  const thinkingDuration = message.thinkingDuration ? `${message.thinkingDuration}秒` : "";
  return (
    <div className="group flex">
      <div className="min-w-0 flex-1 space-y-4">
        {isThinking ? (
          <ThinkingIndicator content={message.thinking} duration={message.thinkingDuration} />
        ) : null}
```

##### 原行51–57：助手分支返回：耗时标签格式化与活动思考指示器（`MessageItem.tsx` L51–L57）
这一组打开助手分支的外层结构。第 51 行把可选的秒数变成展示字符串：有非零值才拼上「秒」，缺失或为 0 得到空串。条件用的是真值判断而不是「不等于 null」，所以 0 秒和「没有耗时」在这里被同等对待——对展示来说这正是想要的，没人需要看到「深度思考 0 秒」。

`return (` 之后是这次渲染的根节点 `<div className="group flex">`：`flex` 让气泡横向排布（左侧留白、右侧内容），`group` 是 Tailwind 的分组钩子，让子元素可以用 `group-hover:` 响应「鼠标悬停在整个气泡上」——反馈按钮默认透明、悬停才显形就是靠它（`FeedbackButtons.tsx:120–126`）。内层 `min-w-0 flex-1 space-y-4` 里的 `min-w-0` 又是那个 flex 陷阱：不写它，内层的最小宽度是内容宽度，超长代码块会把气泡撑出容器、出现横向滚动。

这一行里还有一个三元条件（第 55–57 行）：正在思考时创建思考指示器，并把**未格式化的秒数**和思考原文传进去（指示器自己决定怎么显示计时）；不在思考时返回 null，指示器被卸载。判断依据是 24 行的 `isThinking`，也就是 Store 在 `appendThinkingContent` 里写的那个布尔（5.6），不是「thinking 字符串非空」。

紧随其后的 58–91 行是「思考已结束、但仍有思考文本」时的可折叠面板，这里不引用源码，但事实要留住：外层条件是「不在思考、且思考文本去掉首尾空白后仍非空」；面板头是一个 type 为 button 的按钮（避免被当成表单的默认提交按钮），点击时用函数式更新把前一状态取反，而不是用 render 时捕获的展开值；头部显示固定文案「深度思考」，有耗时时再显示一个耗时徽标；右侧下箭头图标的类名用 cn 组合基础类与展开时的旋转类，未展开时那个短路表达式返回假值、被 cn 丢掉；只有展开值为真时才插入正文，正文就是思考原文，容器用保留换行的白色空间规则展示，所以思考里的分点与换行不会塌成一段。

实际触发什么？教学输入里 `isThinking=false`、`thinking` 为空，这两个条件都为假，于是 51–91 行的所有内容都不产生任何 DOM；`thinkingExpanded` 这个 `useState` 也从未被点击，永远停在 `false`。真实使用中，思考阶段 Store 会把 `isThinking` 置真、`thinkingStartAt` 记时间，正文开始后第一次 `appendStreamContent` 把 `isThinking` 置假并补上 `thinkingDuration`（5.6 的 519–521 行），那一刻指示器被卸载、折叠面板出现——同一个组件里两个条件交接。

不这样写会怎样？如果面板只判「思考文本非空」，思考进行中就会出现两个思考区（活动指示器 + 折叠面板）叠在一起；如果点击时用捕获的展开值直接取反，连续快速点两次时两次都用旧值，可能只切换一次，表现为「点了没反应」；如果去掉按钮的 type 声明，它一旦出现在 form 里就会触发提交。

这一组两条整组事实。框架契约：`useState` 的 setter 接收函数时，React 会把**最新**状态作为实参传进去并在同一次更新里排队，这比闭包捕获的值可靠；同一事件里的多次函数式更新会依次应用。底层与设计：思考面板的展开状态属于「这条消息的局部 UI 状态」，放组件里而不放 Store，是因为它不该触发整页重渲染，也不该持久化——刷新后折叠是默认行为。

```tsx
export function MarkdownRenderer({ content, messageId, sources }: MarkdownRendererProps) {
  const theme = useThemeStore((state) => state.theme);
  const citationIndexes = React.useMemo(
    () => resolveCitationIndexes(content, sources),
    [content, sources]
  );

  return (
    <ReactMarkdown
      remarkPlugins={[
        [remarkGfm, { singleTilde: false }],
        remarkCjkFriendly,
        [remarkPlainSourceCitations, { indexes: citationIndexes }],
        remarkNormalizeCitations
      ]}
```

##### 原行174–188：渲染器入口：主题 selector、引用索引缓存与四个 remark 插件（`MarkdownRenderer.tsx` L174–L188）
这一组是 Markdown 管线的起点。`export function MarkdownRenderer({ content, messageId, sources }: MarkdownRendererProps)` 从 props 解构三个字段——`content` 是全文，`messageId` 用于角标，`sources` 是可选来源数组。这是纯函数式组件，整个函数体只做两件事：算两个派生值，然后交给 `ReactMarkdown`。

`const theme = useThemeStore((state) => state.theme);` 是第二个「正确使用 selector」的现场（第一个是 5.7.1 的 `recommendReveal`）。为什么这里必须用 selector？因为主题是**全局**状态，而每条消息、每个代码块都要读它；如果写成 `useThemeStore()`，那么切换主题时整页每个组件都会重渲染，而真正需要重渲染的只是代码块的高亮配色。用 selector 之后，订阅的粒度变成「theme 这个字符串」，其它全局字段变化不惊动它。注意 selector 返回的是字符串，`Object.is` 比较天然可靠，不会出现「每次返回新对象」的坑。

`const citationIndexes = React.useMemo(() => resolveCitationIndexes(content, sources), [content, sources]);` 缓存引用索引的推导。`useMemo` 的语义是「依赖没变就复用上次的值」：两个依赖都是字符串/数组引用，字符串按**值**比较（`Object.is("abc", "abc")` 为真），所以只要正文没变，即使重新 render 也不会重算；流式期间 `content` 每个 delta 都换，于是每个 delta 都重算一次。`resolveCitationIndexes`（160–172 行）做的事是：用正则扫出所有 `[N](#cite-N)` 形式的规范角标，把编号收进一个 `Set`；如果一个都没有，直接返回空数组，表示「模型没进入引用模式」；有的话再把 `sources` 里带 `index` 的编号并进去。所以这个数组是「本条回答里应该被渲染成角标的编号集合」，供第四个插件使用。

`remarkPlugins={[...]}` 是四个插件的顺序数组。`[remarkGfm, { singleTilde: false }]` 开 GFM 扩展（表格、删除线、任务列表、自动链接），并把单波浪线关闭——不关的话一个 `~` 会被当成删除线起点，写「大约 3~5 个」这种中文表达就会莫名出现删除线。`remarkCjkFriendly` 处理中日韩文本与 Markdown 语法的冲突（例如中文里的 `**` 强调、全角标点旁边的换行）。`[remarkPlainSourceCitations, { indexes: citationIndexes }]` 把正文里漏写规范的 `[N]`、`【N】` 补齐成角标，但只在 `indexes` 非空时生效——没有引用模式的回答里，`[1]` 保持原样，不会被误升级。`remarkNormalizeCitations` 做最后的规范化。数组顺序即执行顺序，前面的插件改了节点，后面的才看得到。

实际触发什么？`ReactMarkdown` 拿到 `{content}` 这个 child（425 行）与上述配置，内部用 `remark-parse` 把字符串解析成 mdast，用 `remark-rehype` 转 hast，再用 `rehype` 插件处理，最后通过 `components` 映射成 React 元素。整个过程在一次 render 里同步完成；`useMemo` 只是省掉「内容没变时」的重复推导，不影响解析。

不这样写会怎样？把 `useMemo` 的依赖写成 `[]`：正文涨了，角标编号集合还是第一次那份，后出现的 `[2]` 不会被补成角标；依赖写成 `[content]` 而漏掉 `sources`：FINISH 补上来源后，集合里缺 `source.index`，面板里有的来源在正文里没有角标。把 `singleTilde` 打开：中文里常见的 `~` 会被吃掉成删除线。

这一组两条整组事实。框架契约：`useMemo` 只保证「依赖不变时**通常**复用」，React 保留在内存压力下丢弃缓存的权利，所以它不能承载副作用，也不能当作正确性依赖——正确性必须由依赖本身保证。底层与设计：引用索引是从**正文**反推出来的，而不是从 `sources` 直接生成，这是因为「渲染哪些角标」取决于模型写没写，而不是后端给了几条来源；两者不一致时以正文为准。顺带一句：这个组件里的三个 selector 与缓存都不涉及网络，任何一次重算都发生在浏览器主线程上，所以「什么时候重算」直接决定流式时的流畅度。

```tsx
      rehypePlugins={[rehypeRaw, rehypeSanitize]}
      components={{
        code({ className, children, node, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          const language = match?.[1] || "text";
          const value = String(children).replace(/\n$/, "");

          // react-markdown v9 不再提供 inline 属性；没有换行时按内联代码展示
          if (!value.includes("\n")) {
```

##### 原行189–197：rehype 白名单与代码组件判定：语言前缀正则、缺省 text、裁掉尾换行（`MarkdownRenderer.tsx` L189–L197）
这一组把配置从「解析」推进到「元素映射」。插件数组里两个 rehype 插件的顺序有实质意义：rehypeRaw 先把 Markdown 里内嵌的 HTML 解析成 hast 元素，rehypeSanitize 再按默认白名单（GitHub 那套 schema）过滤标签、属性与协议。顺序颠倒就等于「先过滤纯文本、再把裸 HTML 解析出来」，过滤完全失效。这条链的存在说明项目确实允许模型输出部分 HTML，同时用白名单兜住脚本与事件属性。

`components` 对象里用一个自定义的 code 组件替换所有代码元素——行内代码与围栏代码块都会进这个函数，react-markdown 不区分两者。形参里类名来自代码元素上的 language 前缀，`children` 是代码文本，`node` 是 hast 节点本身；`node` 被单独解构出来是刻意的：它不能作为 DOM 属性传给元素，否则 React 会对未知属性告警，而 `...props` 会把剩余的合法属性原样透传。

第 192 行用正则从类名里抠语言标识，只认字母、数字与下划线组成的前缀，所以 `language-c++`、`language-objective-c` 这类带符号的标识匹配不到，`match` 为 `null`；类名缺失时用空串兜底，避免 `exec` 报错。第 193 行用可选链取捕获组，缺失时退回 `"text"`——`||` 在这里同时兜住 `null` 与空串。`"text"` 是 Prism 的合法语言名，表示不高亮、按纯文本渲染。

第 194 行把子节点强制转成字符串，再**只裁掉一个结尾换行**。为什么要裁：`mdast-util-to-hast` 在生成代码节点的文本时会先给值补一个换行（`node_modules/mdast-util-to-hast/lib/handlers/code.js:18`），不裁掉的话 Prism 会把这一行当成空行渲染，代码块底部多出一条空行，复制出来的文本也带尾换行。只裁一个、不用 `trim()`，是因为代码内部的缩进与空行有意义，`trim()` 会把首行的缩进一起吃掉，Python 代码会直接语法错位。

紧接着的 196 行是一条注释，它记录了这段代码最反直觉的一点：react-markdown v9 不再给自定义组件传 `inline` 属性，所以「这是行内代码还是代码块」只能靠内容反推——没有换行就当行内，有换行就当代码块。这个启发式会有边界，下一组和「同输入局部运行」会给出实测。

实际触发什么？模型输出以三个反引号加 ts 开头的围栏代码块时：`rehypeRaw`/`rehypeSanitize` 不改变代码内容（代码里的 `<` 已是文本节点），`code` 组件收到 `className="language-ts"` 与以 `\n` 结尾的文本，正则取到 `ts`，裁掉一个尾换行，`value` 里有换行 → 走代码块分支（下一组）。行内代码 `` `useMemo` `` 进来时 `className` 是 `undefined`，`value` 里没有换行 → 走行内分支。

不这样写会怎样？去掉 `rehypeSanitize`：模型输出 `<img src=x onerror=...>` 会在浏览器里真的执行，这是最容易理解的一条安全边界。去掉 `\n` 裁剪：代码块底部多一条空行、复制按钮复制出的文本多一个换行。把 `replace(/\n$/, "")` 换成 `trim()`：首行缩进丢失，粘贴到编辑器里缩进全乱。把 `\w+` 放宽成 `.+`：`language-c++` 能拿到 `c++`，但 Prism 没有这个语言名，会退化成不高亮——功能上等价，只是少一次「猜错」。

这一组两条整组事实。框架契约：`rehype` 插件按数组顺序执行，`rehype-raw` 负责「解析原始 HTML」、`rehype-sanitize` 负责「按 schema 过滤」，两者必须成对且有序；`react-markdown` v9 的 `components` 覆盖发生在 hast→React 的映射阶段，拿到的是 hast 节点，不是 mdast。底层与设计：把 `node` 与其余 props 分开，是「元数据不进 DOM」的通用做法；`...props` 透传则保证 `className` 之外的属性（例如 `data-*`）不丢。

```tsx
          return (
            <div className="my-3 overflow-hidden rounded-md border border-[#d0d7de] bg-[#f6f8fa] dark:border-[#30363d] dark:bg-[#161b22]">
              <div className="flex items-center justify-between border-b border-[#d0d7de] bg-[#f6f8fa] px-3 py-1.5 dark:border-[#30363d] dark:bg-[#161b22]">
                <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-[#57606a] dark:text-[#8b949e]">
                  {language}
                </span>
                <CopyButton value={value} />
```

##### 原行212–218：代码块分支：表头语言标签加复制入口，正文交给 Prism 高亮（`MarkdownRenderer.tsx` L212–L218）
这一组是代码块分支的开头。`return (` 之后的最外层是一个带圆角与边框的 `div`，`my-3` 控制上下留白，`overflow-hidden` 让内部滚动区不破坏圆角；在这个容器里再分两层：一层是表头，一层是代码区。表头 `div` 用 `flex items-center justify-between` 把语言标签推到左边、复制按钮推到右边；标签 `span` 的类名里 `font-mono` 让语言名用等宽字体、`text-[11px]` 与 `uppercase` 让 `ts`、`python` 这类小写标识以大写形态出现——纯视觉，不改变值。

`{language}` 就是上一组算出来的标识，缺省值是 `"text"`，所以没有语言标注的代码块表头显示 `TEXT`。`<CopyButton value={value} />` 把裁掉尾换行的代码文本交给复制按钮，复制按钮是独立组件、自己管理「刚复制过」的短暂状态（430–457 行）；它只出现在代码块分支里，行内代码没有复制入口。

紧随其后的 219–238 行闭合表头、开一个 `overflow-x-auto` 的容器，放入 `SyntaxHighlighter`：`language={language}`、`style={theme === "dark" ? oneDark : oneLight}`（这正是入口处 selector 取 `theme` 的下游用途）、`PreTag="div"`（避免嵌套 `<pre>`，因为外层已经是自定义容器）、`customStyle` 里把背景设成透明、边距清零、字号 13px、行高 1.5，`showLineNumbers={false}`、`wrapLines={true}`，最后把 `{value}` 作为高亮文本。也就是说：**高亮器拿到的是被裁过一次尾换行的完整代码**，每次 `content` 变化它都会重新做一遍语法分析。

`theme === "dark"` 这个判据本身也值得说明：它读的是 Store 里的字符串，而不是 CSS 的 `prefers-color-scheme`，所以主题切换会立刻反映到代码配色上；但也意味着「跟随系统」这件事必须在别处（主题 Store 初始化时）决定，渲染层不再判断系统偏好。

实际触发什么？围栏代码块进入这个分支后，DOM 结构是「容器 → 表头（语言 + 复制按钮）→ 横向滚动区 → Prism 渲染出的 `<div>` 与若干 `<span class="token …">`」。复制按钮的 `value` 是纯文本代码，不含任何高亮标签，所以复制结果是可粘贴的源码。

不这样写会怎样？把 `PreTag` 留在默认的 `pre`，外层自定义 `div` 里就会出现 `<div><pre>…</pre></div>` 的嵌套，`customStyle` 的 margin 与外层留白叠加，代码块上下出现双倍空隙。把 `wrapLines` 设为 `false`，长代码行不会折行，只能横向滚动——虽然外层已有 `overflow-x-auto`，但行内高亮的背景色在滚动时会断掉。把 `theme` 直接写死 `oneLight`，暗色主题下代码块会是白底。

这一组两条整组事实。框架契约：`react-syntax-highlighter` 的 `Prism` 导出是一个受控的展示组件，`style` 是 JS 对象主题而不是 CSS 类，切换主题等于换一份内联样式；它不做增量更新，文本变了就整体重算 token。底层与设计：把「语言标签 + 复制按钮」放在表头而不是悬浮在代码右上角，是为了在横向滚动时它们保持可见——代码区的滚动不会带走表头。

```tsx
  const handleCopy = async (mode: "text" | "markdown") => {
    markInteracted();
    cancelCopyTimer();
    setCopyOpen(false);
    const value = mode === "markdown" ? content : markdownToPlainText(content);
    try {
      await navigator.clipboard.writeText(value);
      toast.success(mode === "markdown" ? "已复制 Markdown" : "复制成功");
    } catch {
      toast.error("复制失败");
    }
  };
```

##### 原行103–114：消息级复制：Markdown 原文与纯文本两种形态，落盘走剪贴板 API（`FeedbackButtons.tsx` L103–L114）
这一组回答「气泡上的复制按钮最终做了什么」。handleCopy 收一个模式参数，先做三件收尾：把按钮从「悬停才显示」切到「保持显示」并取消隐藏定时器、取消下拉菜单的关闭定时器、立刻收起菜单。三件事都在 await 之前同步完成——用户点完菜单项，菜单必须马上消失，而剪贴板写入是异步的。

复制成 Markdown 时直接用气泡收到的原文（含 **、#、代码围栏），复制成纯文本时先过一遍 markdownToPlainText（frontend/src/lib/markdownToText.ts 第 5 行：代码围栏脱壳、去掉标题井号与引用符号、去掉列表标记、把图片换成 alt 文本）。content 这个 prop 来自 MessageItem 第 118 行原样传入的 message.content，是完整正文，不是 delta。

await navigator.clipboard.writeText(value) 是浏览器剪贴板 API，返回 Promise；成功后 toast.success 用 sonner 弹全局提示，失败进 catch 弹「复制失败」。toast 是模块级函数，由挂在根部的 Toaster 渲染，所以这里既不 setState，也不影响气泡自身的渲染。

同一组件里还有另一个入口：97–101 行的 handleFeedback 先把按钮钉住，再算 next = feedback === value ? null : value（点同一个按钮等于取消），然后 submitFeedback(messageId, next)。这个 action 在 Store 里先乐观地把对应那条消息的 feedback 换成新值（chatStore.ts:547–551，又是那个只替换一行的 map），再发请求；失败时用保存的 prev 回滚（:561–565）并弹错误。所以「点赞」的即时应答来自本地状态，不来自服务端。

实际触发什么？悬停气泡 → 反馈条显形（group-hover 与 alwaysVisible 配合，120–126 行）→ 点复制图标是纯文本模式；点右侧箭头展开菜单可选「复制为 Markdown」或「复制」→ 剪贴板 → toast。点拇指 → 乐观更新 + 请求 → 失败回滚。

不这样写会怎样？直接把原文当纯文本复制，用户粘到 IM 里会看到一堆 ** 与 #，甚至把代码围栏一起贴进去；反过来两种形态都走纯文本转换，需要保留格式的用户就复制不到 Markdown。把反馈写成「先请求、成功后改状态」，按钮会明显延迟，用户连点，进而产生重复请求。

这一组两条整组事实。框架契约：navigator.clipboard 只在安全上下文（https 或 localhost）可用，且需要用户手势触发；被拒绝时 Promise 以 NotAllowedError reject，不会抛同步异常，所以必须 await 或 catch。底层与设计：气泡只做「取值 + 调 action」，不加业务判断；messageId 是唯一的业务凭据，正文只用于剪贴板——这条边界让反馈与复制各自演进。

#### 同输入局部运行与实际重要失败

Markdown 这一半可以真跑：我用项目里装好的 remark-parse、remark-gfm 与 mdast-util-to-hast（正是 react-markdown 9.1.0 依赖的三层）把四个输入各解析一遍，打印 code 元素的语言类名与文本子节点。四行结果如下（实测整理，示意，不是项目源码）：

````text
A 未闭合围栏，内容 const a = 1;   → 类名 language-ts，文本 "const a = 1;\n"
B 同内容但围栏闭合               → 类名 language-ts，文本 "const a = 1;\n"
C 两行代码的闭合围栏             → 文本 "const a = 1;\nconst b = 2;\n"
D 行内代码 useMemo               → 无类名，文本 "useMemo"
````

这两个推论都直接决定渲染结果。第一，文本子节点总是带一个结尾换行（mdast-util-to-hast 的 code 处理器给值补换行，见 node_modules/mdast-util-to-hast/lib/handlers/code.js 第 18 行），裁掉一个尾换行之后，单行围栏代码块的值里一个换行都没有——它会命中「没有换行就当行内」的判据，渲染成行内代码，没有表头、没有语言标签、也没有复制按钮。单行代码块在视觉上不是代码块，是启发式的直接后果。第二，未闭合围栏照样解析成带语言类名的代码节点，所以流式中途的多行代码块会提前进入代码块分支，表头与复制按钮先出现，内容是半截。

React 那一半只能推演（仓库没有测试运行器，package.json 只有 dev 与 build）。t1：正文「你」，存在性条件成立、等待条件不成立、非思考，渲染出一个渲染器，解析出单个段落，引用索引为空数组，三个控件条件全假，气泡里只有一段文字。t2：正文「你好」，重新解析，仍是一段。t3：FINISH 到达，状态变 done、id 换成 M-301、来源变成数组、落库状态 NORMAL，三个控件条件同时变真；若正文里有 [1]，引用索引因来源变化而重算，角标从禁用变成可点。t4：点来源按钮 → toggleSourcesPanel → Store 改 openedSourceMessageId → 右侧面板出现。

失败一：单行代码块没有复制入口。用户写一句单行 ts 围栏时，看到的是行内样式，复制按钮不存在。要修就得放弃「有没有换行」这个启发式——v9 虽然不给 inline，但可以看父节点（code 在 pre 里就是代码块），或者按节点位置判断。当前没做，属于已知且被接受的偏差。

失败二：每个 delta 都重新解析全文并重新高亮。正文每帧都变，引用索引缓存失效重算，ReactMarkdown 重新解析整段 Markdown，代码块里的 SyntaxHighlighter 重新跑一遍 Prism；一个回答里有几段代码，每来一个 delta 都把前面所有代码块重新高亮一次。缓解办法是按块缓存（按空行切块，未变化的块复用上次的 React 元素），当前没有做。

失败三：引用角标的中间态。SourceCitation 用「有没有来源与 messageId」决定可不可点（第 29 行）：来源还没到时，渲染层按编号查不到来源，角标是 disabled 胶囊、悬浮没有卡片、点了没反应。流式期间模型已经写出 [1]、来源却要等 FINISH——用户看到「有个角标但点不动」。这是渲染层对未完成的第三种处理：不禁用整块内容，只禁用依赖缺失数据的交互。

失败四：拒绝消息仍然显示反馈按钮。showFeedback（19–23 行）只要求助手、非流式、有真实 id、不是临时前缀，没有检查落库状态；推荐追问的判据额外要求 NORMAL。所以被拒绝的 M-300 会显示复制与点赞点踩、不显示推荐追问。给一条「系统繁忙」点赞，请求被后端按业务规则拒绝，Store 回滚并弹错误——不是崩溃，但界面上有一个注定失败的按钮。

失败五：非空断言依赖前置条件。123 行的非空断言只是编译期声明，运行时不做检查；安全性来自 122 行的来源判据已经确认数量大于零。如果哪天把两层条件拆开，断言就会把 undefined 传给子组件，子组件读长度时抛错——TypeScript 不会拦你，因为断言就是「我保证」。

#### 机制与工程判断

先看四种形态。用户消息是一条纯文本段，没有状态没有控件；助手消息（流式中）可能有点列、活动思考指示器、半截 Markdown，没有控件；助手消息（完成）是正文加可折叠思考面板加四个入口；助手消息（出错）是正文加红字提示，控件按状态判断不显示。四种形态全部由角色、状态、是否思考、正文与思考是否为空算出来，没有第五个「视图状态」字段——视图是消息字段的函数，不引入第二套状态机，也就不会有状态不同步。

再看未完成是在哪几层被处理的。第一层是存在性：正文区与点列各由两个派生布尔控制，半个段落也能显示，因为 Markdown 解析器对不完整语法容错很好（未闭合围栏当成延伸到文末的代码块）。第二层是可操作性：控件统一用「状态不是流式中」把生成中排除在外，复制是例外。第三层是依赖缺失：来源要等 FINISH，角标就先渲染成禁用态；思考耗时徽标也要等第一次正文 delta 才算出来。三层各管一件事，所以没有出现「整个气泡被一个 loading 遮住」的做法。

React 侧三条判断。能派生就不要存：正文有无、等待、三个控件条件全是每次 render 现算的局部常量，没有一个进 useState。该缓存的只有推导：引用索引缓存省的是重复正则扫描，解析本身在 ReactMarkdown 内部，没有缓存接口。该 memo 的是叶子：渲染器故意不 memo（每个 delta 都必须重算），代码块复制按钮是独立组件，它的「已复制」状态与代码块重渲染互不影响。

还有一条成本结构容易被忽略：渲染器每次重算都会重建整个 components 对象（187 行的对象字面量），里面的 code、a、img 每次都是新引用；ReactMarkdown 用它们渲染节点，新引用意味着内部元素类型每帧都在变——对 React 来说类型变了等于卸载重建子树。实践中表现为流式时整段 Markdown 的 DOM 不断被替换，选区与输入法可能被打断。要优化，第一步是把 components 用 useMemo 提到组件外，而不是 memo 整个渲染器。

最后是「没有重新生成」的边界。推荐追问看起来最接近「再来一次」，但它的语义是问一个新问题（sendMessage(question)，RecommendedQuestions.tsx 第 79–83 行），会新建一条用户消息和一条助手消息，而不是替换当前回答。想加真正的重新生成，缺的不是按钮，而是「重发同一条用户消息、复用或删除当前助手行、处理已落库的旧回答」这一整套 Store 逻辑。

#### 怎么用、上下游、接入与修改影响

上游：MessageItem 的唯一输入是 Message 对象，字段分别是角色（分支）、正文（累积全文）、思考三件套、前端渲染状态、落库状态、来源、反馈、推荐面板状态。它们由 5.6 的 Store 与 5.7.1 的列表维护，组件只读不写；唯一的写操作通过四个入口交给 Store。

四个入口的接线：复制走组件内 handleCopy 到剪贴板，不经过 Store；点赞点踩走 submitFeedback，由 Store 乐观更新再发请求；来源走 SourcesButton 到 toggleSourcesPanel，改 openedSourceMessageId 后右侧面板出现；推荐追问走推荐按钮到 toggleRecommended 与 loadRecommended，改消息上的推荐字段与 recommendReveal（5.7.1 的滚入效果），点具体问题则 sendMessage。所以「气泡是不是发请求」的准确答案是：复制不发，其余三个都由 Store 里的 action 决定发不发、何时发。

改动影响：把用户分支改成走 Markdown，用户输入的星号、井号、方括号会被误解析，还扩大了裸 HTML 的暴露面；把正文判空改成按长度，模型先吐换行时会短暂出现空白正文区；把错误提示改成 else 分支，出错时会盖掉已收到的正文；给反馈判据加上落库状态，拒绝消息不再显示注定失败的按钮；把尾换行裁剪换成整串裁剪，代码块首行缩进丢失；把 components 用 useMemo 缓存，能减少每帧的子树重建，是目前性价比最高的一处优化。

新增能力：要给代码块加下载按钮，改的是 212–218 那一层表头，值与语言都在手；要按状态禁用复制，改的是反馈按钮与代码块复制按钮两处入参，因为它们是两个独立入口；要加重新生成，得新增 Store action 并处理落库与历史，渲染层只负责画按钮。

排查顺序：先在 DevTools 里看角色、状态、是否思考、正文四个值，确认该显示的分支条件是否成立；再看正文是否为空或全是空白字符；然后看 Markdown 输入本身（未闭合围栏、单行围栏、波浪线、HTML 标签）；最后才怀疑插件顺序。复制问题单独一条线：先确认页面是不是 https 或 localhost。
