# Willy* Language Specification and Rules

Willy* is a programming environment and domain-specific language designed for controlling a robot named Willy. Willy navigates in a finite 2D grid containing walls, objects of various types/colors, and goals. Willy is equipped with sensors, actuator arms, a basket for holding objects, and navigation capabilities.

---

## 1. World Definition (`begin-world ... end-world`)

A world defines the initial layout, dimensions, variables, and goal criteria. It is defined as:

```willy
begin-world <world_identifier>
    <instruction>*
end-world
```

The instructions permitted within a world definition block are:

### `World <columns> <rows>`
Defines the dimensions of the grid. 
- A world can have at most **one** such instruction.
- If omitted, the default size is `1` column by `1` row.
- Coordinates are 1-indexed (from `1` to `columns` and `1` to `rows`).

### `Wall <direction> from <col0> <row0> to <col1> <row1>`
Defines a wall starting at cell `(col0, row0)` and extending to `(col1, row1)` in the specified direction.
- `<direction>` must be one of: `north`, `east`, `south`, `west`.
- Directions must be consistent with the coordinates:
  - `north`: `col0 == col1` and `row0 <= row1`.
  - `south`: `col0 == col1` and `row0 >= row1`.
  - `east`: `col0 <= col1` and `row0 == row1`.
  - `west`: `col0 >= col1` and `row0 == row1`.
- Coordinates must be within world bounds.

### `Object-type <identifier> of color <color>`
Defines a unique type of object.
- `<color>` must be one of: `red`, `blue`, `magenta`, `cyan`, `green`, `yellow`.

### `Place <n> of <identifier> at <column> <row>`
Places `n` objects of the specified type at grid coordinate `(column, row)`.
- `n` must be a positive decimal integer.
- The object type must be previously defined.
- If multiple instructions place the same object type at the same cell, the total amount is the sum of all placements.

### `Place <n> of <identifier> in basket`
Places `n` objects in Willy's basket.
- `n` must be a positive decimal integer.
- The object type must be previously defined.
- If multiple instructions place the same object type in the basket, the total amount is the sum of all placements.

### `Start at <column> <row> heading <direction>`
Defines Willy's initial position and orientation.
- `<direction>` must be one of: `north`, `east`, `south`, `west`.
- At most **one** start instruction is allowed.
- If omitted, Willy starts at `(1, 1)` heading `north`.

### `Basket of capacity <n>`
Specifies the maximum carrying capacity of Willy's basket.
- At most **one** basket capacity instruction is allowed.
- If omitted, the default capacity is `1` object.

### `Boolean <identifier> with initial value <value>`
Defines a user-defined boolean variable.
- `<value>` must be `true` or `false`.
- Redefining the same boolean variable is a semantic error.

### `Goal <identifier> is <goal-test>`
Defines a named subgoal condition.
- Redefining the same subgoal is a semantic error.
- `<goal-test>` can be one of:
  - `willy is at <column> <row>`
  - `<n> <identifier> objects in basket`
  - `<n> <identifier> objects at <column> <row>`

### `Final goal is <final-goal>`
Defines the final goal condition for completing a task successfully in this world.
- At most **one** final goal instruction is allowed.
- The `<final-goal>` expression is constructed using:
  - Named subgoals or user-defined booleans.
  - Logical operators: `and`, `or`, `not`.
  - Parentheses `( ... )` for precedence grouping.

---

## 2. Program Definition / Tasks (`begin-task ... end-task`)

A task defines a control program to run Willy on a specific world.

```willy
begin-task <task_identifier> on <world_identifier>
    <instruction>*
end-task
```

Instructions in the task block execute sequentially. The program terminates when the last instruction finishes or when the `terminate` instruction is reached.

### Control Flow Instructions

- **Conditionals**:
  - `if <test> then <instruction>`
  - `if <test> then <instruction> else <instruction>`
- **Bounded Iteration**:
  - `repeat <n> times <instruction>` (where `n` is a non-negative integer).
- **Unbounded Iteration**:
  - `while <test> do <instruction>`
- **Compound Blocks**:
  - `begin <instruction>; <instruction>; ... end` (zero or more instructions separated by semicolons).
- **Custom Instruction Definitions**:
  - `define <identifier> as <instruction>`
  - Allows mapping a custom procedure name to an instruction block.
  - Redefining an instruction or overriding a primitive instruction is a semantic error.

### Primitive Action Instructions

- `move`: Moves Willy one step forward in his current direction.
- `turn-left`: Rotates Willy 90 degrees counter-clockwise.
- `turn-right`: Rotates Willy 90 degrees clockwise.
- `pick <identifier>`: Picks up one object of the specified type from the current cell.
  - *Runtime error* if no object of that type exists in the current cell.
  - *Runtime error* if the basket capacity is exceeded.
- `drop <identifier>`: Drops one object of the specified type from Willy's basket onto the current cell.
  - *Runtime error* if Willy does not have the object in his basket.
- `set <identifier>`: Sets a user boolean variable to `true`.
- `set <identifier> to <value>`: Sets a user boolean variable to `true` or `false`.
- `clear <identifier>`: Sets a user boolean variable to `false`.
- `flip <identifier>`: Negates/complements the value of a user boolean variable.
- `terminate`: Immediately halts execution of the task.

---

## 3. Boolean Conditions (`<test>`)

Boolean conditions for task control flow (`if`, `while`) are constructed from:

### Primitive Sensors
- `front-clear`: `true` if there is no wall/boundary in front of Willy.
- `left-clear`: `true` if there is no wall/boundary to Willy's left.
- `right-clear`: `true` if there is no wall/boundary to Willy's right.
- `looking-north`: `true` if Willy is facing north.
- `looking-east`: `true` if Willy is facing east.
- `looking-south`: `true` if Willy is facing south.
- `looking-west`: `true` if Willy is facing west.

### Sensor Expressions
- `found(<identifier>)`: `true` if the current cell contains at least one object of the specified type.
- `carrying(<identifier>)`: `true` if Willy's basket contains at least one object of the specified type.
- User-defined booleans: The name of any boolean variable declared in the world.

### Logical Operators
- `<test0> and <test1>`
- `<test0> or <test1>`
- `not <test>`
- `( <test> )`
