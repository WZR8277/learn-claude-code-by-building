# s14 Evidence

## Automated Tests

```text
conda run -n LearnClaudeCode pytest -q tests/test_s14_cron_scheduler.py
.........                                                                [100%]
9 passed in 0.92s
```

```text
conda run -n LearnClaudeCode pytest -q tests/test_s02_tool_use.py tests/test_s13_background_tasks.py tests/test_s14_cron_scheduler.py
.................                                                        [100%]
17 passed in 0.88s
```

```text
conda run -n LearnClaudeCode pytest -q
........................................................................ [ 79%]
...................                                                      [100%]
91 passed in 0.91s
```

## Runtime Demonstration

```text
conda run -n LearnClaudeCode python -c 'from datetime import datetime; from unittest.mock import patch; import mini_claude_code.cron_scheduler as cs; cs.reset_cron_state();
with patch.object(cs.random, "randint", return_value=314):
    print(cs.run_schedule_cron("10 9 * * 1", "check build", recurring=False, durable=False))
print("queued before:", cs.has_cron_queue())
print("fired:", [job.id for job in cs.fire_due_jobs(datetime(2026, 7, 20, 9, 10))])
print("queued after:", cs.has_cron_queue())
for job in cs.consume_cron_queue():
    print("inject:", f"[Scheduled] {job.prompt}")
print("listed:", cs.run_list_crons())'
Scheduled cron_000314: '10 9 * * 1' -> check build
queued before: False
fired: ['cron_000314']
queued after: True
inject: [Scheduled] check build
listed: No cron jobs. Use schedule_cron to add one.
```

## Notes

- The runtime demo is offline and does not call the model API.
- It proves that a one-shot cron job can be scheduled, fired into `cron_queue`, consumed once, and rendered as `[Scheduled] ...`.
