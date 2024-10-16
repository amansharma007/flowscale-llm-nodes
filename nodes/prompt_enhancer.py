import openai

class PromptEnhancer:
    """
    A ComfyUI custom node that enhances a prompt using the OpenAI API.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "openai_api_key": ("STRING", {"multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "enhance_prompt"
    CATEGORY = "Utilities"

    def enhance_prompt(self, prompt, openai_api_key):
        openai.api_key = openai_api_key
        print(openai.api_key)

        try:
            # Use the OpenAI API to enhance the prompt
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"Improve the following prompt for better image generation:\n\n{prompt}",
                max_tokens=10000,
                temperature=0.7,
                n=1,
                stop=None,
            )

            print(response.choices[0])

            enhanced_prompt = response.choices[0].text.strip()
            print(enhanced_prompt)
            return (enhanced_prompt,)

        except Exception as e:
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
                "openai_api_key": ("STRING", {"multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING", "CONDITIONING")
    RETURN_NAMES = ("enhanced_prompt", "enhanced_conditioning")
    FUNCTION = "enhance_prompt_with_conditioning"
    CATEGORY = "Utilities"

    def enhance_prompt_with_conditioning(self, prompt, conditioning, openai_api_key):
        openai.api_key = openai_api_key

        try:
            # Use the OpenAI API to enhance the prompt
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"Improve the following prompt for better image generation:\n\n{prompt}",
                max_tokens=10000,
                temperature=0.7,
                n=1,
                stop=None,
            )

            enhanced_prompt = response.choices[0].text.strip()

            # Generate new conditioning using the CLIPTextEncode node
            clip_text_encoder = CLIPTextEncode()
            enhanced_conditioning = clip_text_encoder.encode(enhanced_prompt)

            return (enhanced_prompt, enhanced_conditioning)

        except Exception as e:
            return (f"Error: {str(e)}", conditioning)


# Register the node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "Prompt Enhancer": PromptEnhancer,
    "Prompt Enhancer with Conditioning": PromptEnhancerWithConditioning
}
