from openai import OpenAI
import boto3
import json
import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_S3_REGION", "us-east-1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class PromptEnhancer:
    """
    A ComfyUI custom node that enhances a prompt using the OpenAI API.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True}),
                "prompt": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "enhance_prompt"
    CATEGORY = "Utilities"

    def enhance_prompt(self, prompt, base_prompt):
        client = OpenAI(
            api_key = OPENAI_API_KEY
        )

        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"{base_prompt}\n\n{prompt}"
                    }
                ],
                model="gpt-3.5-turbo",
            )

            enhanced_prompt = response.choices[0].message.content
            return (enhanced_prompt,)

        except Exception as e:
            print("Ran into issues")
            print(str(e))
            return (f"Error: {str(e)}",)

class PromptEnhancerWithConditioning:
    """
    A ComfyUI custom node that enhances a prompt using the OpenAI API,
    accepts initial conditioning, and outputs new conditioning.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "conditioning": ("CONDITIONING", ),
            }
        }

    RETURN_TYPES = ("STRING", "CONDITIONING")
    RETURN_NAMES = ("enhanced_prompt", "enhanced_conditioning")
    FUNCTION = "enhance_prompt_with_conditioning"
    CATEGORY = "Utilities"

    def enhance_prompt_with_conditioning(self, prompt, conditioning):
        client = OpenAI(
            api_key = OPENAI_API_KEY
        )

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Improve the following prompt for better image generation:\n\n{prompt}"
                    }
                ],
                model="gpt-3.5-turbo",
            )

            enhanced_prompt = response.choices[0].message.content

            # Generate new conditioning using the CLIPTextEncode node
            clip_text_encoder = CLIPTextEncode()
            enhanced_conditioning = clip_text_encoder.encode(enhanced_prompt)

            return (enhanced_prompt, enhanced_conditioning)

        except Exception as e:
            return (f"Error: {str(e)}", conditioning)

class BedrockPromptEnhancer:
    """
    A ComfyUI custom node that enhances a prompt using AWS Bedrock models.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True}),
                "prompt": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "enhance_prompt"
    CATEGORY = "Utilities"

    def enhance_prompt(self, base_prompt, prompt):
        model = "mistral.mixtral-8x7b-instruct-v0:1"
        try:
            # Initialize the Bedrock client
            bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name="us-east-1",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            )

            # Prepare the prompt for the model
            if model.startswith("anthropic"):
                # For Anthropic models like Claude
                bedrock_prompt = {
                    "prompt": f"\n\nHuman: {base_prompt}:\n\n{prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 500,
                    "temperature": 0.7,
                    "stop_sequences": ["\n\nHuman:"]
                }
            elif model.startswith("ai21"):
                # For AI21 models like Jurassic-2
                bedrock_prompt = {
                    "prompt": f"{base_prompt}:\n\n{prompt}",
                    "maxTokens": 500,
                    "temperature": 0.7,
                    "stopSequences": []
                }
            else:
                # Default handling, assuming Amazon Titan or other models
                bedrock_prompt = f"{base_prompt}: {prompt}"

            formatted_prompt = f"<s>[INST] {bedrock_prompt} [/INST]"

            body = json.dumps({
                "prompt": formatted_prompt,
                "temperature": 0.7,
                "max_tokens": 400,
                "top_p": 0.7,
                "top_k": 50
            })

            # Call the Bedrock model
            response = bedrock_client.invoke_model(
                modelId=model,
                body=body
            )

            # Parse the response
            response_body = response['body'].read()
            response_json = json.loads(response_body)

            print(response_json)

            if model.startswith("anthropic"):
                enhanced_prompt = response_json.get('completion', '').strip()
            elif model.startswith("ai21"):
                enhanced_prompt = response_json['completions'][0]['data']['text'].strip()
            else:
                # Default parsing for other models
                enhanced_prompt = response_json.get('outputs')[0]['text']

            return (enhanced_prompt,)

        except Exception as e:
            return (f"Error: {str(e)}",)

# Register the node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "Prompt Enhancer": PromptEnhancer,
    "Prompt Enhancer with Conditioning": PromptEnhancerWithConditioning,
    "Bedrock - Prompt Enhancer": BedrockPromptEnhancer
}
