# s10 Evidence

## Automated Tests

```text
conda run -n LearnClaudeCode pytest -q tests/test_s10_system_prompt.py
4 passed in 0.97s
```

```text
conda run -n LearnClaudeCode pytest -q
61 passed in 1.09s
```

## Runtime Demonstration

```text
conda run -n LearnClaudeCode python -c 'from mini_claude_code.system_prompt import assemble_system_prompt, get_system_prompt, reset_system_prompt_cache; base={"workspace":"/demo","enabled_tools":["bash","read_file"],"skill_catalog":"(no skills found)","memory_index":""}; print("memory section before:", "Memories available:" in assemble_system_prompt(base)); with_memory=dict(base, memory_index="- [repo](repo.md) — Repository facts"); print("memory section after:", "Memories available:" in assemble_system_prompt(with_memory)); reset_system_prompt_cache(); print("cache stable:", get_system_prompt(with_memory) == get_system_prompt(dict(with_memory)))'
memory section before: False
memory section after: True
cache stable: True
```

## Notes

- The runtime demo is offline and does not call the model API.
- It proves the S10 mechanism directly: memory section loading follows runtime context, and repeated equivalent contexts hit a stable prompt result.
