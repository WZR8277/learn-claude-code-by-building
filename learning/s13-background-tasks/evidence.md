# s13 Evidence

## Automated Tests

```text
conda run -n LearnClaudeCode pytest -q tests/test_s13_background_tasks.py
.....                                                                    [100%]
5 passed in 0.94s
```

```text
conda run -n LearnClaudeCode pytest -q
........................................................................ [ 87%]
..........                                                               [100%]
82 passed in 0.91s
```

## Runtime Demonstration

```text
conda run -n LearnClaudeCode python -c 'from types import SimpleNamespace; import time; from mini_claude_code.background import reset_background_tasks, start_background_task, collect_background_results; reset_background_tasks(); block=SimpleNamespace(type="tool_use", id="toolu_demo", name="bash", input={"command":"pytest tests", "run_in_background": True}); bg_id=start_background_task(block, {"bash": lambda **kwargs: "demo tests passed"}); print("started:", bg_id); notifications=[]
for _ in range(20):
    notifications=collect_background_results()
    if notifications: break
    time.sleep(0.01)
print(notifications[0])'
started: bg_0001
<task_notification>
  <task_id>bg_0001</task_id>
  <status>completed</status>
  <command>pytest tests</command>
  <summary>demo tests passed</summary>
</task_notification>
```

## Notes

- The runtime demo is offline and does not call the model API.
- It proves that a background task receives a stable `bg_id` and later becomes a `<task_notification>`.

## Feishu

- Home Feishu child: `https://jcneiirfaiic.feishu.cn/wiki/GnbrwjTpEicMVWkSbhsc0oxxnkR`
- Parent directory updated: S13 is marked complete and S14 is marked as the next chapter.
