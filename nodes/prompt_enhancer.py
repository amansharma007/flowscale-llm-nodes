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

        try:
            # Use the OpenAI API to enhance the prompt
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Improve the following prompt for better image generation:\n\n{prompt}",
                max_tokens=100,
                temperature=0.7,
                n=1,
                stop=None,
            )

            enhanced_prompt = response.choices[0].text.strip()
            return (enhanced_prompt,)

        except Exception as e:
            return (f"Error: {str(e)}",)

# Register the node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "Prompt Enhancer": PromptEnhancer
}
