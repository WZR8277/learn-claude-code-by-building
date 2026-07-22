# s11 Evidence

## Automated Tests

```text
conda run -n LearnClaudeCode pytest -q tests/test_s11_error_recovery.py
8 passed in 0.81s
```

```text
conda run -n LearnClaudeCode pytest -q
69 passed in 0.89s
```

## Runtime Demonstration

```text
conda run -n LearnClaudeCode python -c 'exec("""from mini_claude_code.error_recovery import RecoveryState, with_retry, retry_delay, ESCALATED_MAX_TOKENS
import os
calls = [RuntimeError("529 overloaded"), RuntimeError("529 overloaded"), RuntimeError("529 overloaded"), "ok"]
state = RecoveryState("primary")
os.environ["FALLBACK_MODEL_ID"] = "fallback"
def flaky():
    value = calls.pop(0)
    if isinstance(value, Exception):
        raise value
    return value
result = with_retry(flaky, state, sleep=lambda delay: None)
print("retry result:", result)
print("current model:", state.current_model)
print("sample delay:", round(retry_delay(2, retry_after=3), 1))
print("escalated max tokens:", ESCALATED_MAX_TOKENS)
""")'
retry result: ok
current model: fallback
sample delay: 3
escalated max tokens: 64000
```

## Notes

- The runtime demo is offline and does not call the model API.
- It proves the S11 recovery helpers directly: 529 retry can switch to a fallback model, Retry-After is respected, and the output-token escalation budget is available.
