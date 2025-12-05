# Ficheros usados en CienaLLM

Escojo del TFM de jvela las configuraciones que indica

En todos ellos:
* summarization: False
* response_parsing: True
* self_criticis: False

|Configuration| LLM| Prompt Techniques| F1 Score| Parse Error| Rate Exec. Time (s/article)|
|-|-|-|-|-|-|
| Best-F1| qwen_72b| CoT + DESC| 0.878| 0.000| 35.792|
| FASTEST| qwen_3b| DESC |0.726 |0.000| 2.633| 
| Efficient| qwen_7b| —| 0.844| 0.000| 3.243|

## Fastest

**qwen3b + DESC** - 'model_qwen2.5:3b-instruct-q4_K_M/summarization_False/response_parsing_True/self_criticism_False/cot_False/impact_prompt_category_description' 


## Efficent

**qwen_7b** - 'model_qwen2.5:7b-instruct-q4_K_M/summarization_False/response_parsing_True/self_criticism_False/cot_False/impact_prompt_category_simple'

## Best-F1
**qwen_72b + CoT + Desc** - '/model_qwen2.5:72b-instruct-q4_K_M/summarization_False/response_parsing_True/self_criticism_False/cot_True/impact_prompt_category_description'


