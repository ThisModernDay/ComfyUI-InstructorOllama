import json
import os
import importlib.util
from typing import Type
from pydantic import BaseModel
import instructor
from openai import OpenAI
from ollama import Client
from server import PromptServer # type: ignore[import]
from aiohttp import web

routes = PromptServer.instance.routes
@routes.post('/ollama/get_models')
async def get_models_endpoint(request):
    print("Received request to get Ollama models")
    data = await request.json()
    url = data.get("url")
    client = Client(host=url)
    models = [model['name'] for model in client.list().get('models', [])]
    
    return web.json_response(models)

class OllamaInstructorNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ollama_base_url": ("STRING", {"default": "http://127.0.0.1:11434"}),
                "ollama_model": ((), {}),
                "user_prompt": ("STRING", {"multiline": True}),
                "system_prompt": ("STRING", {"multiline": True}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "max_retries": ("INT", {"default": 3, "min": 1, "max": 10}),
                "response_model": (cls.get_available_models(), {}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_structured_output"
    CATEGORY = "Instructor/Ollama"

    @staticmethod
    def get_available_models():
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        model_files = [f[:-3] for f in os.listdir(models_dir) if f.endswith('.py') and not f.startswith('__')]
        return model_files

    @staticmethod
    def load_model(model_name: str) -> Type[BaseModel]:
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        model_path = os.path.join(models_dir, f"{model_name}.py")
        
        spec = importlib.util.spec_from_file_location(model_name, model_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Assuming the model class name is the same as the file name
        return getattr(module, model_name)

    def generate_structured_output(self, ollama_base_url, ollama_model, user_prompt, system_prompt, temperature, max_retries, response_model):
        
        client = instructor.from_openai(OpenAI(api_key="ollama", base_url=f"{ollama_base_url}/v1", max_retries=max_retries), mode=instructor.Mode.JSON)

        # Load the selected response model
        model_class = self.load_model(response_model)

        system_prompt = {
            'role': 'system',
            'content': system_prompt
        }

        user_prompt = {
            'role': 'user',
            'content': user_prompt
        }

        
        try:
            # Generate structured output using Instructor and Ollama
            response = client.chat.completions.create(
                model=ollama_model,
                messages=[system_prompt, user_prompt],
                response_model=model_class,
                temperature=temperature
            )

            # Convert the response to a JSON string
            result = json.dumps(response.dict(), indent=2)
            return (result,)

        except Exception as e:
            raise Exception(f"Failed to generate output after {max_retries} attempts: {str(e)}")
        
# This function is required for ComfyUI to recognize and load the custom node
NODE_CLASS_MAPPINGS = {
    "OllamaInstructorNode": OllamaInstructorNode
}

# This dictionary provides human-readable names for the custom nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaInstructorNode": "Ollama Instructor Node"
}