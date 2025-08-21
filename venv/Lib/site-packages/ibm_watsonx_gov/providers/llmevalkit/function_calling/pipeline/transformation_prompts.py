from typing import Dict, Any, List
from copy import deepcopy

# ──────────────────────────────────────────────────────────────────────────────
# 1) extract_units
# ──────────────────────────────────────────────────────────────────────────────


SINGLE_PARAM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "user_value": {
            "type": ["string", "null"],
            "description": (
                "The exact substring the user provided for this parameter, always as a raw string. "
                "Examples:\n"
                "  - Time quantities: '30 seconds', '2 ms', '1.5 hours'\n"
                "  - Data sizes: '1000 MB', '2 GB', '512 bytes'\n"
                "  - Temperatures: '25°C', '77°F'\n"
                "  - Dates: 'December 1st, 2024', '2024-06-20'\n"
                "  - Numbers: '0.75', '42'\n"
                "  - Identifiers: '550e8400-e29b-41d4-a716-446655440000'\n"
                "If the user did not mention this parameter, return `null`."
            ),
        },
        "user_units_or_format": {
            "type": ["string", "null"],
            "description": (
                "The canonical unit or format attached to `user_value`, normalized to lowercase, singular form, "
                "and using standard abbreviations. If none, return an empty string ''.\n"
                "Examples:\n"
                "  - Time: 'second', 'millisecond', 'hour', 'day'\n"
                "  - Data: 'byte', 'kilobyte', 'megabyte', 'gigabyte'\n"
                "  - Temperature: 'celsius', 'fahrenheit', 'kelvin'\n"
                "  - Length: 'meter', 'centimeter', 'inch'\n"
                "  - Weight: 'kilogram', 'gram', 'pound'\n"
                "  - Currency: 'usd', 'eur', 'jpy'\n"
                "  - Date formats: 'yyyy-mm-dd', 'month day, year', 'iso8601'\n"
                "  - Identifiers: 'uuid', 'hex'\n"
                "If the user_value has no unit/format, return ''."
            ),
        },
        "spec_units_or_format": {
            "type": ["string", "null"],
            "description": (
                "The canonical unit or format defined or implied by the parameter's JSON Schema, "
                "normalized to lowercase and singular form, using the same conventions as `user_units_or_format`. "
                "Examples: 'second', 'byte', 'yyyy-mm-dd', 'uuid'.\n"
                "If the spec and user_value use the same unit/format, return exactly that same canonical string for both. "
                "If the schema specifies no unit/format, return ''."
            ),
        },
    },
    "required": ["user_value", "user_units_or_format", "spec_units_or_format"],
}


def build_multi_extract_units_schema(params: List[str]) -> Dict[str, Any]:
    """
    Construct a JSON Schema whose top-level properties are each parameter name.
    Each parameter maps to an object matching SINGLE_PARAM_SCHEMA.
    """
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": params.copy(),
    }
    for pname in params:
        schema["properties"][pname] = deepcopy(SINGLE_PARAM_SCHEMA)
    return schema


# -------------------------------------------------------------------
# 2) System prompt template for multi-parameter unit/format extraction
# -------------------------------------------------------------------
# We include a `{schema}` placeholder, which will be replaced at runtime
# with a JSON-dumped version of the schema built for the current params.
MULTI_EXTRACT_UNITS_SYSTEM: str = """\
You are an expert in natural language understanding and API specifications.
Given:
  1. A user context (natural-language instructions).
  2. A JSON Schema snippet that describes **all** parameters the tool expects.
  3. A list of all parameter names.

Your task:
  For each parameter name, identify:
    - The raw "user_value" mentioned in the user context (as a string).
    - The "user_units_or_format" explicitly or implicitly attached to that value.
      (If none, return an empty string `""`.)
    - The "spec_units_or_format" defined or implied by the JSON Schema (type/description).
      (If none, return an empty string `""`.)

Respond with exactly one JSON object whose keys are the parameter names,
and whose values are objects with "user_value", "user_units_or_format", and "spec_units_or_format".
The JSON must match this schema exactly:

{schema}
"""


# -------------------------------------------------------------------
# 3) User prompt template for multi-parameter unit extraction
# -------------------------------------------------------------------
# Use Python .format(...) placeholders for:
#   context        = The conversation/context string
#   full_spec      = JSON.dumps(...) of the combined JSON Schema snippet for all params
#   parameter_names = Comma-separated list of parameter names
MULTI_EXTRACT_UNITS_USER: str = """\

Examples (multi-parameter):

1) Context: "Change the interval to 30 seconds and set threshold to 0.75."
   Full Spec:
   {{
     "type": "object",
     "properties": {{
       "interval": {{
         "type": "integer",
         "description": "Interval duration in seconds"
       }},
       "threshold": {{
         "type": "number",
         "description": "Threshold limit (0.0 to 1.0)"
       }}
     }},
     "required": ["interval", "threshold"]
   }}
   Parameter names: "interval, threshold"
   -> {{
        "interval": {{
          "user_value":"30",
          "user_units_or_format":"second",
          "spec_units_or_format":"second"
        }},
        "threshold": {{
          "user_value":"0.75",
          "user_units_or_format":"",
          "spec_units_or_format":""
        }}
      }}

2) Context: "Download up to 2 GB of data and retry 5 times."
   Full Spec:
   {{
     "type": "object",
     "properties": {{
       "size": {{
         "type": "string",
         "description": "Size limit in bytes"
       }},
       "retries": {{
         "type": "integer",
         "description": "Maximum retry count"
       }}
     }},
     "required": ["size", "retries"]
   }}
   Parameter names: "size, retries"
   -> {{
        "size": {{
          "user_value":"2",
          "user_units_or_format":"gigabyte",
          "spec_units_or_format":"byte"
        }},
        "retries": {{
          "user_value":"5",
          "user_units_or_format":"",
          "spec_units_or_format":""
        }}
      }}

3) Context: "Set backup_date to December 1st, 2024 and limit to 100MB."
   Full Spec:
   {{
     "type": "object",
     "properties": {{
       "backup_date": {{
         "type": "string",
         "format": "date",
         "description": "Date of backup in YYYY-MM-DD"
       }},
       "limit": {{
         "type": "string",
         "description": "File size cap (in bytes)"
       }}
     }},
     "required": ["backup_date", "limit"]
   }}
   Parameter names: "backup_date, limit"
   -> {{
        "backup_date": {{
          "user_value":"December 1st, 2024",
          "user_units_or_format":"month day, year",
          "spec_units_or_format":"yyyy-mm-dd"
        }},
        "limit": {{
          "user_value":"100",
          "user_units_or_format":"megabyte",
          "spec_units_or_format":"byte"
        }}
      }}

Context:
{context}

Full Spec (JSON Schema snippet for all parameters):
{full_spec}

Parameter names: {parameter_names}

Please return exactly one JSON object matching the schema defined in the system prompt.
"""

# ──────────────────────────────────────────────────────────────────────────────
# 2) generate_transformation_code
# ──────────────────────────────────────────────────────────────────────────────

# System prompt for code generation
GENERATE_CODE_SYSTEM: str = """\
You are an expert Python engineer. Generate a self-contained Python module that converts between arbitrary units or formats. Your code must define exactly two functions:

1. transformation_code(input_value: str) -> <transformed_type>  
   - **Purpose**: Convert a string in OLD_UNITS into its equivalent in TRANSFORMED_UNITS.  
   - **Behavior**:  
     - Parse the numeric or textual content from `input_value` (e.g. “10 ms”, “December 1st, 2011”).  
     - Attach the OLD_UNITS and perform a conversion to TRANSFORMED_UNITS using standard Python libraries (e.g. `pint`, `datetime`/`dateutil`, or built-ins).  
     - Return the result as the specified `<transformed_type>` (e.g. `int`, `float`, `str`, `list[float]`, etc.).  
   - **Error Handling**: If parsing or conversion is unsupported, raise a `ValueError` with a clear message.

2. convert_example_str_transformed_to_transformed_type(transformed_value: str) -> <transformed_type>  
   - **Purpose**: Parse a raw string in the example transformed format into the same `<transformed_type>`.  
   - **Behavior**:  
     - Strip any non-numeric or formatting characters as needed.  
     - Return the parsed value.  
   - **Error Handling**: If parsing fails, raise a `ValueError`.

You will be provided with the following information:
- OLD UNITS: The units or format of the input value (e.g., "millisecond", "celsius", "yyyy-mm-dd").
- EXAMPLE FORMAT OF OLD VALUE: An example string in the OLD UNITS (e.g, "1000 ms", "25°C", "December 1st, 2011").
- TRANSFORMED UNITS: The units or format of the transformed value (e.g., "second", "kelvin", "unix timestamp").
- EXAMPLE FORMAT OF TRANSFORMED VALUE: An example string (may not be fully representative - therefore you should only take in account the units when implementing the transformation logic) in the TRANSFORMED UNITS (e.g., "10 s", "[298.15]", "1322697600").
- TRANSFORMED TYPE: The type of the transformed value (e.g., `int`, `float`, `str`, `list[float]`).

Your response must be a valid Python script that defines the two functions above, with no additional text or formatting.
The script should be self-contained and runnable in a standard Python environment without any external dependencies (except for standard libraries).
If the transformation is not supported or possible with the standard Python libraries, return an empty string in the generated_code field.
Respond with ONLY a JSON object matching this schema (no Markdown fences, no extra text):
{
  "generated_code": "<full python script>"
}"""


generated_code_example1 = (
    "from datetime import datetime, timezone\n"
    "import dateutil.parser\n\n"
    "def transformation_code(input_value: str) -> int:\n"
    '    """\n'
    "    Convert a date string with the format 'month day, year' to a unix timestamp.\n\n"
    "    Args:\n"
    "        input_value (str): The date string to convert.\n\n"
    "    Returns:\n"
    "        int: The unix timestamp representing the date.\n\n"
    "    Example:\n"
    "        >>> transformation_code('December 1st, 2011')\n"
    "        1322697600\n"
    '    """\n\n'
    "    # Parse the date string, dateutil.parser automatically handles 'st', 'nd', 'rd', 'th'\n"
    "    dt = dateutil.parser.parse(input_value)\n\n"
    "    # Ensure the datetime is treated as UTC\n"
    "    dt = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)\n\n"
    "    # Convert to Unix timestamp\n"
    "    return int(dt.timestamp())\n\n"
    "def convert_example_str_transformed_to_transformed_type(transformed_value: str) -> int:\n"
    '    """\n'
    "    Convert a string representation of a unix timestamp to an integer.\n\n"
    "    Args:\n"
    "        transformed_value (str): The string representation of the unix timestamp.\n\n"
    "    Returns:\n"
    "        int: The unix timestamp as an integer.\n\n"
    "    Example:\n"
    "        >>> convert_example_str_transformed_to_transformed_type('1322697600')\n"
    "        1322697600\n"
    '    """\n\n'
    "    # Strip any whitespace and convert to integer\n"
    "    transformed_value = transformed_value.strip()\n"
    "    return int(transformed_value)\n"
)

transformation_eval_example1 = (
    """
### Example 1:

OLD UNITS: month day, year
EXAMPLE FORMAT OF OLD VALUE: 'December 1st, 2011'
TRANSFORMED UNITS: unix timestamp
EXAMPLE FORMAT OF TRANSFORMED VALUE: '1322697600'
TRANSFORMED TYPE: int

RESPONSE:
{{"""
    + '"generated_code": "'
    + generated_code_example1
    + '"'
    + """}}"""
)

generated_code_example2 = (
    "def transformation_code(input_value: str) -> float:\n"
    '    """\n'
    "    Convert a string in milliseconds to seconds.\n\n"
    "    Args:\n"
    "        input_value (str): The input value in milliseconds.\n\n"
    "    Returns:\n"
    "        float: The converted value in seconds.\n\n"
    "    Example:\n"
    "        >>> transformation_code('1000 ')\n"
    "        1.0\n"
    '    """\n\n'
    "    return float(input_value.strip()) / 1000\n\n"
    "def convert_example_str_transformed_to_transformed_type(transformed_value: str) -> float:\n"
    '    """\n'
    "    Convert a string representation of seconds to a float.\n\n"
    "    Args:\n"
    "        transformed_value (str): The string representation of the value in seconds.\n\n"
    "    Returns:\n"
    "        float: The converted value in seconds.\n\n"
    "    Example:\n"
    "        >>> convert_example_str_transformed_to_transformed_type('10 ')\n"
    "        10.0\n"
    '    """\n\n'
    "    return float(transformed_value.strip())\n"
)

transformation_eval_example2 = (
    """
### Example 2:

OLD UNITS: millisecond
EXAMPLE FORMAT OF OLD VALUE: '1000 '
TRANSFORMED UNITS: second
EXAMPLE FORMAT OF TRANSFORMED VALUE: '10 '
TRANSFORMED TYPE: float

RESPONSE:
{{"""
    + '"generated_code": "'
    + generated_code_example2
    + '"'
    + """}}"""
)

generated_code_example3 = (
    "def transformation_code(input_value: str) -> list[float]:\n"
    '    """\n'
    "    Convert a temperature string in Celsius to Kelvin.\n\n"
    "    Args:\n"
    "        input_value (str): The temperature in Celsius.\n\n"
    "    Returns:\n"
    "        list[float]: The converted temperature in Kelvin as a list.\n\n"
    "    Example:\n"
    "        >>> transformation_code('25°C')\n"
    "        [298.15]\n"
    '    """\n\n'
    "    # Remove the '°C' suffix and convert to float\n"
    "    input_value = input_value.strip()[:-2]\n"
    "    # Convert Celsius to Kelvin (K = C + 273.15)\n"
    "    kelvin_value = float(input_value) + 273.15\n"
    "    # Return as a list with one element\n"
    "    return [kelvin_value]\n\n"
    "def convert_example_str_transformed_to_transformed_type(transformed_value: str) -> list[float]:\n"
    '    """\n'
    "    Convert a string representation of a temperature in Kelvin to a list of floats.\n\n"
    "    Args:\n"
    "        transformed_value (str): The temperature in Kelvin as a string.\n\n"
    "    Returns:\n"
    "        list[float]: The converted temperature in Kelvin as a list.\n\n"
    "    Example:\n"
    "        >>> convert_example_str_transformed_to_transformed_type('[35]')\n"
    "        [35.0]\n"
    '    """\n\n'
    "    # Remove the brackets and convert to float\n"
    "    transformed_value = transformed_value.strip()[1:-1]\n"
    "    # Return as a list with one element\n"
    "    return [float(transformed_value)]\n"
)

transformation_eval_example3 = (
    """
### Example 3:

OLD UNITS: celsius
EXAMPLE FORMAT OF OLD VALUE: '25°C'
TRANSFORMED UNITS: kelvin
EXAMPLE FORMAT OF TRANSFORMED VALUE: '[35]'
TRANSFORMED TYPE: list

RESPONSE:
{{"""
    + '"generated_code": "'
    + generated_code_example3
    + '"'
    + """}}"""
)

transformation_eval_example4 = """
### Unsupported Transformation Example:

OLD UNITS: unit1
EXAMPLE FORMAT OF OLD VALUE: ABC
TRANSFORMED UNITS: unit2
EXAMPLE FORMAT OF TRANSFORMED VALUE: DEF
TRANSFORMED TYPE: str

RESPONSE:
{{"generated_code": ""}}"""


# User prompt template for code generation
# Use Python format-style placeholders:
#   transformation_eval_examples, old_value, old_units, transformed_value, transformed_units, transformed_type
GENERATE_CODE_USER: str = (
    f"""\
Few-shot examples for how to convert:

{transformation_eval_example1}

{transformation_eval_example2}

{transformation_eval_example3}

{transformation_eval_example4}

"""
    + """\

TASK:

OLD UNITS: {old_units}
EXAMPLE FORMAT OF OLD VALUE: {old_value}
TRANSFORMED UNITS: {transformed_units}
EXAMPLE FORMAT OF TRANSFORMED VALUE: {transformed_value}
TRANSFORMED TYPE: {transformed_type}

RESPONSE:
"""
)

# JSON Schema dict for validation
GENERATE_CODE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "generated_code": {
            "type": "string",
            "description": "The generated Python code for the transformation. Should be a valid Python script without any Markdown formatting.",
        }
    },
    "required": ["generated_code"],
}
