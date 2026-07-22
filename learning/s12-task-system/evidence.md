# s12 Evidence

## Automated Tests

```text
conda run -n LearnClaudeCode pytest -q tests/test_s12_task_system.py
8 passed in 0.92s
```

```text
conda run -n LearnClaudeCode pytest -q
77 passed in 1.02s
```

## Runtime Demonstration

```text
conda run -n LearnClaudeCode python -c 'exec("""import tempfile
from pathlib import Path
import mini_claude_code.task_system as ts
with tempfile.TemporaryDirectory() as d:
    ts.TASKS_DIR = Path(d)
    schema = ts.create_task("schema")
    api = ts.create_task("api", blockedBy=[schema.id])
    print("initial can_start api:", ts.can_start(api.id))
    print(ts.claim_task(schema.id))
    print(ts.complete_task(schema.id))
    print("after schema can_start api:", ts.can_start(api.id))
    print("files:", len(list(Path(d).glob("*.json"))))
""")'
initial can_start api: False
Claimed task_1784732836_9848 (schema)
Completed task_1784732836_9848 (schema)
Unblocked: api
after schema can_start api: True
files: 2
```

## Notes

- The runtime demo is offline and does not call the model API.
- It proves the S12 task graph behavior directly: a dependent task starts blocked, completing the upstream task reports the downstream task as unblocked, and task state is persisted as JSON files.
