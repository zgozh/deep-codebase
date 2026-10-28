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
