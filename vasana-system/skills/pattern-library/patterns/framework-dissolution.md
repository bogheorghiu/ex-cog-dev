# Framework Dissolution

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

**Principle**: Every framework both enables and constrains. Know when to transcend.

## Core Insight

Frameworks are tools, not identities. They solve common problems elegantly—until they don't. When a framework fights your solution, the problem isn't your code. It's either (1) you're solving the wrong problem, or (2) you've outgrown the framework's assumptions.

## Application

- **Use frameworks as tools, not identities**: "I'm a React developer" → framework prison
- **When framework fights your solution, examine the problem**: Is the framework wrong, or is your approach?
- **Best code often emerges at framework boundaries**: Where you need to go beyond, that's where innovation lives
- **Transcend with understanding, not rebellion**: Know WHY the framework does it that way

## When to Apply

- Framework workarounds multiplying (fighting the framework)
- "Standard" way feels wrong for your use case
- Boilerplate outweighs business logic
- Adding features requires more framework than feature code

## Anti-Patterns to Watch For

❌ **Fighting the Framework**
```python
# Manually registering every tool (framework pattern)
server.register_tool("get_stock_price", get_stock_price)
server.register_tool("get_stock_info", get_stock_info)
server.register_tool("get_stock_analysis", get_stock_analysis)
server.register_tool("get_stock_history", get_stock_history)
# Adding new tool requires updating 3 places
# You're fighting the framework's registration pattern
```

✅ **Transcending the Framework**
```python
# Recognize pattern: framework constrains tool addition
# Solution: dynamic discovery
import os
import importlib

tool_dir = "implementations"
for filename in os.listdir(tool_dir):
    if filename.endswith('.py'):
        module = importlib.import_module(f"{tool_dir}.{filename[:-3]}")
        if hasattr(module, 'execute'):
            server.register_tool(module.TOOL_NAME, module.execute)

# Adding new tool: just drop file in directory
# Framework serves you, not vice versa
```

## Code Example: When to Dissolve

### Stage 1: Framework Serves You
```python
# Flask routing works great for simple CRUD
@app.route('/ticker/<symbol>')
def get_ticker(symbol):
    return jsonify(fetch_ticker(symbol))

# Framework enables productivity
```

### Stage 2: Framework Constrains You
```python
# Now you need:
# - Different auth per endpoint
# - Rate limiting per user
# - Custom validation per route
# - Async support for some endpoints

@app.route('/ticker/<symbol>')
@auth_required
@rate_limit
@validate_symbol
@async_handler
def get_ticker(symbol):
    # More framework than feature
```

### Stage 3: Transcend the Framework
```python
# Recognize: HTTP routing is just pattern matching
# Build your own that handles YOUR constraints

class Router:
    def __init__(self):
        self.routes = {}

    def add(self, path, handler, auth=None, rate_limit=None, async_mode=False):
        self.routes[path] = {
            'handler': handler,
            'auth': auth,
            'rate_limit': rate_limit,
            'async': async_mode
        }

    def handle(self, path, request):
        route = self.routes.get(path)
        # Now you control the flow, not the framework
```

## Dissolution Decision Tree

```
Is the framework fighting you?
├─ Yes → Ask: Is my approach wrong?
│   ├─ Yes → Realign with framework
│   └─ No → Framework's assumptions don't fit
│       └─ Transcend: Build what you need
└─ No → Framework is serving you
    └─ Use it gratefully
```

## Transcendence Examples

### Example 1: MCP Tool Registration

**Framework Way:**
```python
# Manual registration for each tool
server.add_tool(ToolSchema(...), handler1)
server.add_tool(ToolSchema(...), handler2)
# N tools = N registration lines
```

**Transcendent Way:**
```python
# Convention over configuration
# Drop file in implementations/, it auto-registers
# Framework boundary dissolved, convention remains
```

### Example 2: ORM Constraints

**Framework Way:**
```python
# ORM wants relationships defined in models
class User(Model):
    posts = relationship('Post', backref='user')

class Post(Model):
    user_id = ForeignKey('user.id')

# Works until you need:
# - Dynamic relationships
# - Cross-database joins
# - Non-standard foreign keys
```

**Transcendent Way:**
```python
# Recognize: ORM is just query builder + object mapping
# Use it for simple queries, raw SQL for complex ones
simple_users = User.query.filter_by(active=True).all()  # ORM

complex_data = db.execute("""
    SELECT u.*, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON ...
    WHERE ...
""")  # Raw SQL when needed

# Best of both worlds
```

## Integration with Other Vasanas

- **Rooted Flight**: Master framework before transcending it
- **Groove-Deepening**: Framework habits can become grooves
- **Concrete↔Abstract**: Framework is abstraction; test against concrete needs

## Recognition Signals

**Framework needs dissolution when:**
- Workarounds proliferate
- Boilerplate exceeds business logic
- Fighting framework patterns regularly
- "The framework way" feels wrong

**Stay in framework when:**
- It solves your problem elegantly
- Conventions speed development
- Community patterns apply
- Transcending would be premature optimization

## Warning: Premature Dissolution

Don't transcend just to be clever:

❌ **Unnecessary Transcendence**
```python
# Reinventing Flask routing "because we can"
# When Flask routing works fine
```

✅ **Necessary Transcendence**
```python
# Building custom routing because we need:
# - Per-endpoint auth strategies
# - Custom rate limiting
# - Framework doesn't support our use case
```

The framework should fight you **consistently** before you transcend, not just once.
