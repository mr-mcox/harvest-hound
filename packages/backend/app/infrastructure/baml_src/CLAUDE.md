# BAML Syntax Guide for Claude Code

BAML (Basically, A Made-Up Language) is a domain-specific language for building LLM prompts as functions and creating agentic workflows.

## Core Concepts

BAML files define structured schemas and functions that call LLMs with type-safe inputs and outputs. The generated client code can be used in Python, TypeScript, and other languages.

## Schema Definition

### Classes
```baml
class MyObject {
  // Required fields
  name string
  count int
  enabled bool
  score float

  // Optional fields use ?
  description string? @description("Optional description field")

  // Arrays (cannot be optional)
  tags string[]
  numbers int[]

  // Enums (must be declared separately)
  status MyEnum?

  // Union types
  type "success" | "error" | "pending"

  // Nested objects
  metadata MyMetadata

  // Image type
  profileImage image

  // Field-level assertions
  age int @assert(valid_age, {{ this >= 0 and this <= 150 }})

  // Class-level assertions (at bottom of class)
  @@assert(name_length, {{ this.name|length > 0 }})
}
```

### Enums
```baml
enum MyEnum {
  PENDING
  ACTIVE @description("Item is currently active")
  COMPLETE @description("Task has been finished")
}
```

### Key Rules for Schemas
- Use `PascalCase` for class and enum names
- Use `snake_case` or `camelCase` for field names
- Optional fields require `?` suffix
- Arrays cannot be optional
- Enums must be declared separately
- Comments use `//`
- No recursive types or inline definitions

## Function Definition

```baml
function MyFunction(input: MyInputType) -> MyOutputType {
  client "openai/gpt-4o"
  prompt #"
    Your task description here.

    {{ _.role("user") }}
    {{ input }}

    {{ ctx.output_format }}
  "#
}
```

### Available LLM Clients
- `openai/gpt-4o`
- `openai/gpt-4o-mini`
- `anthropic/claude-3-5-sonnet-latest`
- `anthropic/claude-3-5-haiku-latest`

### Prompt Requirements
1. **Always include input**: Use `{{ input }}` to reference function parameters
2. **Always include output format**: Use `{{ ctx.output_format }}` - this automatically generates the schema instructions
3. **Use role tags**: `{{ _.role("user") }}` to indicate user input sections
4. **Don't repeat schema**: Never manually describe the output format - `{{ ctx.output_format }}` handles this

### Prompt Template Syntax
- Variables: `{{ variable_name }}`
- Role indicators: `{{ _.role("user") }}`, `{{ _.role("assistant") }}`
- Output format: `{{ ctx.output_format }}`
- Multi-line strings: `#"..."`

## Complete Example

```baml
// Schema definitions
class TweetAnalysis {
  mainTopic string @description("The primary topic or subject matter")
  sentiment "positive" | "negative" | "neutral"
  isSpam bool @description("Whether the tweet appears to be spam")
  confidence ConfidenceLevel
  hashtags string[]

  @@assert(topic_not_empty, {{ this.mainTopic|length > 0 }})
}

enum ConfidenceLevel {
  HIGH @description("Very confident in the analysis")
  MEDIUM @description("Moderately confident")
  LOW @description("Low confidence, may need review")
}

// Function definition
function AnalyzeTweets(tweets: string[]) -> TweetAnalysis[] {
  client "openai/gpt-4o-mini"
  prompt #"
    Analyze each tweet for topic, sentiment, and spam detection.
    Be thorough but concise in your analysis.

    {{ _.role("user") }}
    Tweets to analyze: {{ tweets }}

    {{ ctx.output_format }}
  "#
}
```

## Compiling

After updating the code, you can generate the client in the target language using the following command from the directory containing baml_src:

```
uv run baml-cli generate
```

## Testing

To run tests defined in BAML, you can run the following command in the directory containing baml_src:

```
uv run baml-cli test
```

Note that these can be stochastic and running them incurs costs.

## Usage in Generated Code

### Python
```python
from baml_client import b
from baml_client.types import TweetAnalysis

# Synchronous call
results = b.AnalyzeTweets(["Hello world!", "Buy crypto now!!!"])
for analysis in results:
    print(f"Topic: {analysis.mainTopic}")
    print(f"Sentiment: {analysis.sentiment}")
```

### TypeScript
```typescript
import { b } from './baml_client'
import { TweetAnalysis } from './baml_client/types'

// Asynchronous call
const results = await b.AnalyzeTweets(["Hello world!", "Buy crypto now!!!"])
results.forEach(analysis => {
  console.log(`Topic: ${analysis.mainTopic}`)
  console.log(`Sentiment: ${analysis.sentiment}`)
})
```

## Best Practices

1. **Schema Design**
   - Use descriptive field names and @description annotations
   - Prefer enums over string unions for better type safety
   - Use assertions for validation instead of LLM-based validation
   - Keep classes focused and not overly complex

2. **Function Design**
   - Choose appropriate LLM client for task complexity
   - Write clear, specific prompts
   - Always include `{{ ctx.output_format }}`
   - Use role tags to structure conversations

3. **Validation**
   - Use `@assert` for field-level validation
   - Use `@@assert` for class-level validation
   - Prefer compile-time validation over runtime validation

4. **Naming Conventions**
   - Functions: `PascalCase`
   - Classes: `PascalCase`
   - Enums: `PascalCase`
   - Fields: `camelCase` or `snake_case`
   - Enum values: `UPPER_CASE`

## Common Patterns

### Image Analysis
```baml
class ImageDescription {
  description string
  objects string[]
  colors string[]
  mood "happy" | "sad" | "neutral" | "energetic"
}

function DescribeImage(image: image) -> ImageDescription {
  client "openai/gpt-4o"
  prompt #"
    Analyze this image and provide a detailed description.

    {{ _.role("user") }}
    {{ image }}

    {{ ctx.output_format }}
  "#
}
```

### Multi-step Analysis
```baml
class InitialAnalysis {
  summary string
  keyPoints string[]
  needsFollowup bool
}

class DetailedAnalysis {
  fullAnalysis string
  recommendations string[]
  confidence ConfidenceLevel
}

function AnalyzeDocument(content: string) -> InitialAnalysis {
  client "openai/gpt-4o-mini"
  prompt #"
    Provide an initial analysis of this document.

    {{ _.role("user") }}
    {{ content }}

    {{ ctx.output_format }}
  "#
}

function DeepAnalyze(content: string, initial: InitialAnalysis) -> DetailedAnalysis {
  client "openai/gpt-4o"
  prompt #"
    Based on the initial analysis, provide a detailed analysis.

    Initial findings: {{ initial }}

    {{ _.role("user") }}
    Original content: {{ content }}

    {{ ctx.output_format }}
  "#
}
```
