# 字面读法对照：一句话讲用途，和按类型讲到结果接收

> **这一页的定位。** 它教的不是「一个单元怎么写」（那看 [单元示范](unit-example.md)），而是一件更小的事：**同一段源码，只报用途和讲到类型/求值/结果接收，差在哪里**。写 Java 或任何静态类型语言时，遇到 lambda、泛型、函数值、流式接收这类「读起来知道大概、说不清每一步交出什么」的语句，先按这一页的口径过一遍。
>
> 下文是原样保留的对照例，含反例、逐行组讲解、两个值的演算与版本边界。链接的 `AsyncGreeting.java` 是自编 Java SE 17 教学样例，不属于任何目标项目源码，不与项目事实混用。

## 语句精读对照：Java 函数值与结果接收

本节是独立 Java 对照例，不依赖任何其他示例或项目上下文。需要讲 Java 函数值和返回结果时，只读本节至文末即可。链接的 `AsyncGreeting.java` 是自编 Java SE 17 样例，不属于目标项目源码。

**反例（原行 10–21）：**“此方法为每个姓名生成问候并返回。”即使附有准确原行标题与源码链接，这句话也只报用途；它没有说明 `List<CompletableFuture<String>>` 怎样变成 `List<String>`、两个 lambda 分别交出什么函数、`join` 何时接收结果，或输入顺序如何保留。下面沿同一源码按行组补足。

独立源码：[AsyncGreeting.java 原行 1–22](../assets/examples/AsyncGreeting.java#L1-L22)。

```java
// Standalone Java example; this is not target-project source.
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;

public final class AsyncGreeting {
    private AsyncGreeting() {
    }

    public static List<String> greet(List<String> names, Executor executor) {
        List<CompletableFuture<String>> jobs = names.stream()
                .map(name -> CompletableFuture.supplyAsync(
                        () -> "Hi " + name,
                        executor
                ))
                .toList();

        return jobs.stream()
                .map(CompletableFuture::join)
                .toList();
    }
}
```

##### 原行 1–4：来源说明与类型导入（[源码](../assets/examples/AsyncGreeting.java#L1-L4)）

注释声明这是教学样例，避免把它误认为目标仓库的源码。三个 import 只让类名在本文件可直接使用：`List` 装有序元素，`CompletableFuture<T>` 表示稍后可取得一个 `T` 结果，`Executor` 接收任务并决定怎样调度。导入类型不会执行并发工作。

##### 原行 6–8：无实例状态的类壳（[源码](../assets/examples/AsyncGreeting.java#L6-L8)）

`AsyncGreeting` 是公开 `final` 类；`final` 禁止其他类继承它。私有空构造器阻止调用者创建实例。本例的方法是 `static`，不依赖实例字段，所以调用者可以直接用类名调用 `greet`。闭合构造器的括号不新增行为；类的最后一个闭合括号见原行 22。

##### 原行 10：读完整个方法签名（[源码](../assets/examples/AsyncGreeting.java#L10-L10)）

`public static List<String> greet(List<String> names, Executor executor)` 中，`public` 让其他类可以调用它，`static` 表示它属于类本身，调用者不必先创建 `AsyncGreeting` 实例。`List<String>` 的尖括号说明列表元素类型是 `String`；`List<CompletableFuture<String>>` 则表示列表元素是 Future，而每个 Future 的结果类型是 `String`。`names` 和 `executor` 按形参位置接收调用时的第一个与第二个实参：前者给姓名，后者给任务执行策略。

##### 原行 11–12：外层 lambda 把一个姓名映射成一个 Future（[源码](../assets/examples/AsyncGreeting.java#L11-L12)）

`names.stream()` 建立一条顺序计算管线，可以白话成“按源顺序逐个处理姓名”；它先描述处理步骤，不会在调用 `stream()` 时就把所有步骤跑完。`map` 会把每个 `String` 元素转换成一个新值。目标类型在这里可读作 `Function<String, CompletableFuture<String>>`，所以 `name -> ...` 左侧是**单个形参**，右侧是映射时执行的表达式：它调用 `supplyAsync(...)` 并产出 Future。整句 `List<CompletableFuture<String>> jobs = ...` 把终止操作得到的 Future 列表赋给 `jobs`；外层 `List`、内层 `CompletableFuture`、最终结果 `String` 三层类型分别描述列表、任务与任务结果。

##### 原行 13–16：零参数 Supplier、捕获值与提交时机（[源码](../assets/examples/AsyncGreeting.java#L13-L16)）

`() -> "Hi " + name` 的 `()` 表示**没有形参**；`+` 在这里把字符串 `"Hi "` 和当前 `name` 连接成一个问候字符串，例如 `Hi Mina`。这整个零参数 lambda 是 `Supplier<String>` 函数值。`supplyAsync(` 的第一个实参是这个 supplier，逗号后的第二个实参 `executor` 指定任务交给谁执行；行末 `))` 依次关闭 `supplyAsync(...)` 和外层 `.map(...)` 调用。该方法返回 `CompletableFuture<String>`，于是外层 map 产出的元素类型成立。创建 lambda 不会计算问候文本；supplier 的方法体由 executor 调用时才运行。`name` 是外层 lambda 的形参，在本方法内未再赋值，所以它是“有效 final”（effectively final），不必显式写 `final`；零参数 lambda 捕获并保留本次映射的 `name`，每项任务使用自己的姓名。原行 16 的 `.toList()` 是终止操作：它消费全部 `names` 流，逐项提交任务并把返回的 Future 收进 `jobs`，此处还没有取出字符串。

JDK 17 的 [Supplier API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/function/Supplier.html)说明它以无参数 `get()` 提供结果；[JLS 17 §15.27 lambda 规则](https://docs.oracle.com/javase/specs/jls/se17/html/jls-15.html#jls-15.27)说明 lambda 先形成目标函数类型，求值 lambda 不等同于立即执行函数体。任务是否在 `supplyAsync` 返回前就开始，仍由 executor 决定。

##### 原行 18–21：方法引用接收 Future 并把结果交给返回值（[源码](../assets/examples/AsyncGreeting.java#L18-L21)）

`jobs.stream()` 的元素现在是 `CompletableFuture<String>`。`::` 是方法引用语法；在 `map` 的目标类型约束下，`CompletableFuture::join` 等价于 `future -> future.join()`：每个流元素成为实例方法的接收者，`join()` 返回该 Future 的 `String`。方法引用被创建时并没有调用 `join`；第二个 `.toList()` 消费流时才逐项调用它。于是流元素从 `CompletableFuture<String>` 变成 `String`，最终 `List<String>` 由 `return` 交给 `greet` 的调用者，例如调用侧的 `List<String> greetings = AsyncGreeting.greet(names, executor);`。Java 17 中 `Stream.toList()` 保留源元素原有顺序（encounter order），并返回不可修改的列表；若 `join()` 遇到异常完成，会抛出非受检异常 `CompletionException`，即签名不要求调用方声明或捕获它，但异常仍会中断当前调用。

用两个名字演算：若 `names` 为 `Mina`、`Kai`，第一段流先得到代表两项工作的 `jobs = [f0, f1]`。即使 `f1` 先完成，Future 列表的位置仍是 `[f0, f1]`；第二段从 `f0.join()` 开始，若它尚未完成就在这里等，然后读取 `f1`，所以结果是 `["Hi Mina", "Hi Kai"]`，顺序来自输入列表而非完成先后。此处调用的是 `stream()`，没有构造并行流。

显式传入 `Executor` 也不等于保证并行。JDK 17 的 [`Executor.execute`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/Executor.html)允许实现在线程池运行、另一个线程运行，或直接在提交者线程运行；单线程 executor 会串行处理，直接 executor 甚至会在 `supplyAsync` 调用内执行 supplier。多线程池只提供重叠执行的机会，不能从方法名或参数类型推出每次都有并行。

失败边界也分两处。若 supplier 抛出异常，该 Future 异常完成；对应的 `join()` 抛 unchecked `CompletionException`，第二个流会中止，方法不会返回部分字符串列表。若 executor 在 `execute` 阶段拒绝任务，JDK 合同允许抛 `RejectedExecutionException`；由调用次序可推知异常可能在第一个 `.toList()` 消费映射时冒出，先前已接受的任务仍可能运行，而本例没有捕获或取消它们。[CompletableFuture Java SE 17 API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/CompletableFuture.html)明确 `supplyAsync` 使用给定 executor，并规定 `join()` 等结果或在异常完成时抛异常。

这里先把所有姓名对应任务提交，再统一等待：第一段 `.toList()` 完成后 `jobs` 已有全部 Future，第二段才逐项 `join`。若改成每个姓名提交后立刻 `join`，调用会先等第一项结束才提交下一项，通常失去多项工作重叠的机会；当前两段写法保留了并发窗口，同时仍按原输入顺序收集结果。它不保证总时长一定缩短，因为 executor 可能串行执行，且首个 Future 未完成时调用线程会停在它的 `join` 上。

版本边界：本文链接并说明 Java SE 17 官方规则。`Stream.toList()` 的 JDK 文档标记为 since 16；Java 15 及更早版本没有此 API，需改用兼容的收集写法。[Stream Java SE 17 API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/Stream.html#toList())、[JLS 17 §15.13 方法引用](https://docs.oracle.com/javase/specs/jls/se17/html/jls-15.html#jls-15.13)。
