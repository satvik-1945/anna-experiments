---
name: calc-helper
description: "Evaluate math expressions, compute percentages, or show calculator history — use for any arithmetic question"
metadata: {"matrix":{"emoji":"🧮","execution_mode":"prompt","category_name":"productivity"}}
---

# Calculator Helper

Use the **calc** Executa tool for all arithmetic. Never guess numbers in your head or approximate — always call the tool.

## When to use this skill

Trigger this skill when the user asks anything involving:

- Basic arithmetic (`2 + 2`, `17 * 23`, `100 / 7`)
- Percentages (`what is 15% of 240?`, `add 8% tax to 50`)
- Order-of-operations expressions (`2 + 3 * 4`)
- Calculation history (`what did I calculate earlier?`, `show recent calculations`)

## How to call the calc tool

The tool name is `calc`. It takes an `action` parameter:

### evaluate

Compute a single expression.

```
action: evaluate
expression: <normalized arithmetic string>
```

**Normalization rules** (apply before calling):

| User says | Normalize to |
|-----------|--------------|
| `15% of 240` | `240 * 15 / 100` |
| `add 8% to 50` | `50 * 1.08` |
| `subtract 10% from 200` | `200 * 0.9` |
| `square root of 144` | `144 ** 0.5` (if the tool supports `**`) |

Supported operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`, parentheses.

### history

Return recent calculations from this session.

```
action: history
limit: 10
```

## Response format

After calling `evaluate`, present the result clearly:

> **Expression:** `2 + 3 * 4`
> **Result:** `14`

If the tool returns an error, explain what went wrong and suggest a corrected expression.

## Examples

**User:** What is 17 times 23?

1. Call `calc` with `action=evaluate`, `expression=17*23`
2. Respond: "17 × 23 = **391**"

**User:** What is 15% of 240?

1. Normalize to `240 * 15 / 100`
2. Call `calc` with that expression
3. Respond: "15% of 240 = **36**"

**User:** Show my recent calculations

1. Call `calc` with `action=history`, `limit=5`
2. List each entry as `expression → result`

## Constraints

- Always use the calc tool for numeric answers — do not compute mentally.
- Reject expressions that are not arithmetic (no variables, no function calls beyond `**`).
- If the user asks for non-arithmetic math (calculus, matrices), explain that this calculator only handles basic expressions.
