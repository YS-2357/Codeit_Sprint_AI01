from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
import torch

def load_llm(model_name: str, generation_config: dict, quant_config: dict):
    if torch.cuda.is_available():
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=quant_config['load_in_4bit'],
            bnb_4bit_use_double_quant=quant_config['use_double_quant'],
            bnb_4bit_quant_type=quant_config['quant_type'],
            bnb_4bit_compute_dtype=getattr(torch, quant_config['compute_dtype']),
            llm_int8_enable_fp32_cpu_offload=quant_config['enable_fp32_offload']
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            trust_remote_code=True,
        )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    pipe = pipeline(
        model=model,
        tokenizer=tokenizer,
        task="text-generation",
        do_sample=True,
        temperature=generation_config["temperature"],
        repetition_penalty=generation_config["repetition_penalty"],
        return_full_text=False,
        max_new_tokens=generation_config["max_new_tokens"],
    )

    return ChatHuggingFace(llm=HuggingFacePipeline(pipeline=pipe))