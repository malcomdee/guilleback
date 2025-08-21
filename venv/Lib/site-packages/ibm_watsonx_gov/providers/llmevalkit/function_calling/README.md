# Function-Calling Reflection Pipeline

This directory implements a full **pre-call reflection** workflow for conversational agents making API (function) calls. It leverages:

- **Static schema checks** - Ensure that calls conform exactly to the API schema and naming rules. 
- **Semantic LLM-driven metrics** - Evaluate the deeper meaning, context alignment, and correctness of calls beyond syntax. 
- **Optional unit-conversion transforms** via code generation 

All LLM and metric logic lives inside this package—no external frameworks are required.

---

## Table of Contents

1. [Syntactic Checks](##yntactic-checks)
2. [Semantic Metrics](#semantic-metrics)
3. [Quickstart](#quickstart)  
4. [Directory Structure](#directory-structure)  
5. [ReflectionPipeline API](#reflectionpipeline-api)  
   - `static_only`  
   - `semantic_sync` / `semantic_async`  
   - `run_sync` / `run_async`  
6. [Example Usage](#example-usage)  
7. [Custom Metrics](#custom-metrics)  
8. [Transform-Enabled Mode](#transform-enabled-mode)  
9. [Error Handling & Logging](#error-handling--logging)  

---


## Syntactic Checks

These catch straightforward, schema-level errors against your API specification:

* **NonExistentFunction**
  
  *Description:* The function name does not appear in the API spec.

  *Mistake Example:* Calling `get_customer_profile` when only `get_user_profile` is defined.

* **NonExistentParameter**
  
  *Description:* One or more parameters are not defined for the chosen function.

  *Mistake Example:* Using `user` in `get_user_profile(user=42)` when the function expects `user_id`.

* **IncorrectParameterType**
  
  *Description:* Provided parameter values do not match the expected types.

  *Mistake Example:* Passing `"true"` (string) to a boolean parameter `is_active`, instead of `true`.

* **MissingRequiredParameter**
  
  *Description:* A required parameter is omitted.

  *Mistake Example:* Calling `list_events(start_date="2025-05-01")` without the required `end_date`.

* **AllowedValuesViolation**
  
  *Description:* A parameter value falls outside its allowed enumeration.

  *Mistake Example:* Passing `"urgent"` to `priority` when only `"low"`, `"medium"`, or `"high"` are allowed.

* **JsonSchemaValidation**

  *Description:* The API call does not conform to the provided JSON Schema

  Note that We flag types errors in **IncorrectParameterType**, and all other validations (that are not type or Enum) are under    **JsonSchemaValidation**.

  *Examples of Checked Constraints:*
    * Numeric constraints: minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf
    * String constraints: minLength, maxLength, pattern, format (e.g., email, date, URI)
    * Array constraints: items, minItems, maxItems, uniqueItems, contains

* **EmptyApiSpec**

  *Description:* There are no API specifications provided or they are invalid

* **InvalidApiSpec**

  *Description:* The API specifications provided are not valid Tool or ToolSpec instances
  
* **InvalidToolCall**
  
  *Description:* The provided ToolCall is not a valid instance of ToolCall

---

# Semantic Metrics

Each semantic metric outputs a JSON object with fields customized in the JSONL definition files:

* **explanation**: Detailed reasoning behind the judgment.
* **evidence**: Exact conversation or spec excerpts supporting the assessment.
* **output**: Numeric rating on a 1-5 scale (5=best, 1=worst).
* **confidence**: Judge's confidence in the assessment (0.0-1.0).
* **correction**: Structured object containing issue types, explanations, and suggested fixes.
* **actionable_recommendation**: Specific developer guidance when issues are detected.

You can add, remove, or modify metrics by editing the JSONL definitions.

### 2.1 Function Selection Metric

Assesses whether this function call correctly implements the user's immediate request as the appropriate next step in the conversation. Compares against all available functions in the tool inventory to determine if the selection aligns with user intent and context.

**Rating Scale:**
- 5: Perfect match for user request
- 4: Good match with minor misalignment
- 3: Adequate match (threshold for acceptability)
- 2: Poor match for user request
- 1: Completely irrelevant function

*Mistake Example:* User: "What time is it in Tokyo?" Call: `translate_text(text="Hello", target_language="en")` instead of `get_time(timezone="Tokyo")`.

### 2.2 Agentic Metric

Evaluates whether a tool call satisfies prerequisite constraints and relationships defined in conversation history and tool inventory. Checks for explicit prerequisites, tool sequencing requirements, redundancy, parameter completeness, and parameter value relationships.

**Rating Scale:**
- 5: All agentic constraints satisfied
- 4: Minor insignificant issues that don't block execution
- 3: Significant issues requiring additional information
- 2: Major issues preventing proper execution
- 1: Completely inappropriate given context

*Mistake Example:* User: "Translate 'Hola' to English." Call: `translate_text(text="Hola", target="en")` when the tool description explicitly requires a prior call to `detect_language(text="Hola")`.

### 2.3 Grounding Metrics

#### 2.3.1 General Parameter Value Grounding

Assesses whether ALL parameter values in a function call are directly supported by conversation history or API specifications. Identifies hallucinated values, missing information, format errors, and contradictory values.

**Rating Scale:**
- 5: All parameter values correctly grounded and formatted
- 4: Some values may need more information but not hallucinated
- 3: Some values hallucinated or have format errors
- 2: Multiple values incorrect or contradictory
- 1: All values incorrect or missing

*Mistake Example:* User: "Fetch my profile." Call: `get_user_profile(user_id=42)` when no user ID was mentioned in conversation or available from context.

#### 2.3.2 Individual Parameter Hallucination Check

Evaluates whether a SPECIFIC parameter value is grounded in evidence or hallucinated. Checks sources, format compliance, value relationships, and default handling.

**Rating Scale:**
- 5: Perfectly grounded in conversation or documented defaults
- 4: Mostly grounded with minimal inference
- 3: Ambiguously grounded requiring substantial inference
- 2: Mostly ungrounded with tenuous connection
- 1: Completely hallucinated with no basis

*Mistake Example:* User: "Fetch my latest tweets." Call: `get_tweets(username="elonmusk", count=20)` when count was not specified by user and has no documented default.

#### 2.3.3 Value Format Alignment

Checks if a specific parameter value exactly conforms to required type, format, and unit conventions in the API specification.

**Rating Scale:**
- 5: Perfect alignment with specified type, format, units
- 4: Minor deviation unlikely to affect function
- 3: Moderate deviation that might affect function
- 2: Major deviation likely to cause function failure
- 1: Complete mismatch certain to cause failure

*Mistake Example:* User: "Start a countdown for 5 minutes." Call: `set_timer(duration="300000")` instead of `set_timer(duration="5 minutes")`.

## Use Cases

For different use cases, we suggest to execute different metrics, as follows:

### Fast Track Single-Turn

Execute (1) function selection (2) global parameter value grounding

### Slow Track Single-Turn

Execute (1) function selection (2) per-parameter hallucination check (3) per-parameter value format check

### Fast Track Agentic

Execute (1) function selection (2) global agentic metric (3) global parameter value grounding

### Slow Track Agentic

Execute (1) function selection (2) global agentic metric (3) per-parameter hallucination check (4) per-parameter value format check

---

**Customization:** Modify metrics, thresholds, and fields by editing your JSONL configuration files.

---

## Quickstart

```bash
pip install llmevalkit[litellm]  # or your preferred extras
```

```python
from llmevalkit.llm.registry import get_llm
from llmevalkit.function_calling.pipeline.pipeline import ReflectionPipeline

# 1) Pick your LLM provider and initialize clients
MetricsClient = get_llm("litellm.watsonx.output_val")
CodegenClient = get_llm("litellm.watsonx.output_val")
metrics_client = MetricsClient(model_name="meta-llama/llama-3-3-70b-instruct")
codegen_client = CodegenClient(model_name="meta-llama/llama-3-3-70b-instruct")

# 2) Create pipeline (loads bundled metrics JSONL by default)
pipeline = ReflectionPipeline(
    metrics_client=metrics_client,
    codegen_client=codegen_client,
    transform_enabled=False
)

# 3) Define your API specs (OpenAI-style function definitions)
apis_specs = [
    { "type":"function", "function": { ... } },
    ...
]

# 4) Provide a tool_call and context
call = {
  "id":"1","type":"function",
  "function":{"name":"get_weather","arguments":{"location":"Berlin"}}
}
context = "User: What's the weather in Berlin?"

# 5) Run end-to-end reflection
result = pipeline.run_sync(
    conversation=context,
    inventory=apis_specs,
    call=call,
    continue_on_static=False,
    retries=2
)
print(result.model_dump_json(indent=2))
```

---

## Directory Structure

```
src/llmevalkit/function_calling/
├── __init__.py
├── metrics/                <- MetricPrompt templates & JSONL definitions
│   ├── base.py
│   ├── loader.py
│   ├── function_call/
│   │   ├── general.py
│   │   └── general_metrics.jsonl
│   ├── function_selection/
│   │   ├── function_selection.py
│   │   └── function_selection_metrics.jsonl
│   └── parameter/
│       ├── parameter.py
│       └── parameter_metrics.jsonl
├── pipeline/
│   ├── adapters.py         <- API-spec / call normalization
│   ├── pipeline.py         <- High-level ReflectionPipeline
│   ├── semantic_checker.py <- Core LLM metrics orchestration
│   ├── static_checker.py   <- JSONSchema-based validation
│   ├── transformation_prompts.py <- Unit-conversion prompts
│   └── types.py            <- Pydantic models for inputs & outputs
└── examples/
    └── function_calling/
        └── pipeline.py     <- Complete runnable example
```

---

## ReflectionPipeline API

### Initialization

```python
ReflectionPipeline(
    metrics_client: LLMClient,
    codegen_client: LLMClient,
    transform_enabled: bool = False,
    general_metrics: Optional[Path] = None,
    function_metrics: Optional[Path] = None,
    parameter_metrics: Optional[Path] = None,
    transform_examples: Optional[Dict[str,str]] = None,
)
```

- **`metrics_client`**: llmevalkit LLM client for semantic metrics (e.g. output-validating OpenAI or LiteLLM).  
- **`codegen_client`**: llmevalkit LLM client for code generation (required if `transform_enabled=True`).  
- **`*_metrics`**: override paths to your own JSONL metric definitions (otherwise uses `metrics/.../*.jsonl`).  
- **`transform_enabled`**: whether to run unit-conversion checks.  

### `static_only(conversation, inventory, call) → StaticResult`

- Runs pure JSON-schema validation on `call` against `inventory` specs.  
- Checks required parameters, types, enums, etc.

### `semantic_sync(conversation, inventory, call, retries=1) → SemanticResult`

- Runs LLM-driven metric evaluations **synchronously**.  
- Returns per-category semantic results.

### `semantic_async(conversation, inventory, call, retries=1, max_parallel=10) → SemanticResult`

- Same as above, but issues LLM calls in parallel.

### `run_sync(conversation, inventory, call, continue_on_static=False, retries=1) → PipelineResult`

- Full pipeline:  
  1. Static checks  
  2. Semantic metrics (if static passes or `continue_on_static=True`)  
  3. Aggregates final `PipelineResult` with `static`, `semantic`, and `overall_valid`.  

### `run_async(...)`

- Asynchronous equivalent of `run_sync`.

---

## Example Usage

See `examples/function_calling/pipeline/example.py` for a complete, runnable demo:

```bash
python examples/function_calling/pipeline/example.py
```

It will:

1. Define three sample functions (`get_weather`, `create_event`, `translate_text`).  
2. Initialize Watsonx clients.  
3. Run sync reflection for valid and invalid calls.  
4. Print nicely formatted JSON results.

---

## Custom Metrics

By default we ship three JSONL files under `metrics/...`:

- **General**: overall call quality  
- **Function-Selection**: was the right function chosen?  
- **Parameter**: correctness of each parameter value  

Each line in a `.jsonl` file is a JSON object:

```jsonc
// general_metrics.jsonl
{"name":"Clarity", "description":"Rate clarity of the intent","schema":{...},
 "thresholds":{"output":[0,1],"confidence":[0,1]},
 "examples":[
   {"user_kwargs":{...}, "output":{...}}
 ]}
```

To add your own:

1. Create a new `.jsonl` in any folder.  
2. Pass its path into the pipeline constructor:

   ```python
   pipeline = ReflectionPipeline(
     metrics_client=...,
     codegen_client=...,
     general_metrics="path/to/my_general.jsonl",
     function_metrics="path/to/my_func.jsonl",
     parameter_metrics="path/to/my_param.jsonl",
   )
   ```

3. Follow the same JSONL format:  
   - `schema`: valid JSON-Schema object  
   - `thresholds`: dict of numeric field thresholds  
   - `examples`: few-shot examples validating against that schema  

---

## Transform-Enabled Mode

If you want automated unit conversions:

```python
pipeline = ReflectionPipeline(
  metrics_client=metrics_client,
  codegen_client=codegen_client,
  transform_enabled=True,
  transform_examples=my_transform_examples_dict,
)
```

- Uses two additional LLM prompts (in `transformation_prompts.py`):  
  1. **Extract units** from context  
  2. **Generate transformation code**  

- Finally executes the generated code in-process and reports a `TransformResult` per parameter.

---

## Error Handling & Logging

- Each stage wraps exceptions with clear, contextual messages.  
- The LLM clients emit optional hooks (`hooks=[...]`) for tracing or metrics.  
- In semantic phases, malformed or missing fields result in per-metric errors rather than crashing the entire pipeline.

---

Enjoy robust, end-to-end reflection on your function calls—static and semantic—powered entirely by `llmevalkit`!
