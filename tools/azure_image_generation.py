"""
title: Azure Image Generation
description: Generate images using Azure FLUX.2-pro, DALL-E, or other image models
author: MAGI
version: 1.2.0
license: MIT
"""

import os
import requests
import base64
from typing import Optional, Callable, Any
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        AZURE_COGNITIVE_ENDPOINT: str = Field(
            default="",
            description="Azure Cognitive Services endpoint"
        )
        AZURE_API_KEY: str = Field(
            default="",
            description="Azure API Key"
        )
        DEPLOYMENT_NAME: str = Field(
            default="FLUX.2-pro",
            description="Azure deployment name for image generation"
        )
        API_VERSION: str = Field(
            default="preview",
            description="API version"
        )
        DEFAULT_SIZE: str = Field(
            default="1024x1024",
            description="Default image size"
        )
        DEFAULT_QUALITY: str = Field(
            default="standard",
            description="Image quality (standard or hd)"
        )
        TIMEOUT_SECONDS: int = Field(
            default=180,
            description="Request timeout in seconds"
        )
        DEFAULT_STYLE: str = Field(
            default="natural",
            description="Default image style (natural or vivid)"
        )
        OPTIONS_COUNT: int = Field(
            default=2,
            description="Number of images to generate for options/variations"
        )
        SHOW_METADATA: bool = Field(
            default=True,
            description="Show generation metadata (size, model) in output"
        )

    def __init__(self):
        self.valves = self.Valves(
            AZURE_COGNITIVE_ENDPOINT=os.getenv("AZURE_COGNITIVE_ENDPOINT", ""),
            AZURE_API_KEY=os.getenv("AZURE_OPENAI_API_KEY", ""),
            DEPLOYMENT_NAME=os.getenv("AZURE_IMAGE_DEPLOYMENT", "FLUX.2-pro"),
            API_VERSION=os.getenv("AZURE_IMAGE_API_VERSION", "preview"),
            DEFAULT_SIZE=os.getenv("AZURE_IMAGE_SIZE", "1024x1024"),
            DEFAULT_QUALITY=os.getenv("AZURE_IMAGE_QUALITY", "standard"),
            TIMEOUT_SECONDS=int(os.getenv("AZURE_IMAGE_TIMEOUT", "180")),
            DEFAULT_STYLE=os.getenv("AZURE_IMAGE_STYLE", "natural"),
            OPTIONS_COUNT=int(os.getenv("AZURE_IMAGE_OPTIONS_COUNT", "2")),
            SHOW_METADATA=os.getenv("AZURE_IMAGE_SHOW_METADATA", "true").lower() == "true"
        )
        
        # Aspect ratio presets
        self.size_presets = {
            "square": "1024x1024",
            "landscape": "1792x1024",
            "portrait": "1024x1792",
            "wide": "1792x1024",
            "tall": "1024x1792"
        }

    async def generate_image(
        self,
        prompt: str,
        size: str = "",
        style: str = "",
        __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Generate an image from a text description using Azure FLUX.2-pro.
        
        :param prompt: Detailed description of the image to generate. Be specific about style, colors, composition, lighting, and subject matter.
        :param size: Image dimensions - 1024x1024 (square), 1792x1024 (landscape), 1024x1792 (portrait), or presets: 'square', 'landscape', 'portrait', 'wide', 'tall'
        :param style: Image style - 'natural' for realistic or 'vivid' for dramatic/artistic (uses default from valves if empty)
        :return: The generated image displayed inline
        """
        if __event_emitter__:
            await __event_emitter__({"type": "status", "data": {"description": "🎨 Generating image...", "done": False}})
        
        endpoint = self.valves.AZURE_COGNITIVE_ENDPOINT.rstrip('/')
        deployment = self.valves.DEPLOYMENT_NAME
        api_version = self.valves.API_VERSION
        api_key = self.valves.AZURE_API_KEY
        
        # Handle size presets
        if size and size.lower() in self.size_presets:
            size = self.size_presets[size.lower()]
        elif not size:
            size = self.valves.DEFAULT_SIZE
        
        # Use default style if not specified
        if not style:
            style = self.valves.DEFAULT_STYLE

        if not api_key:
            return "❌ Error: Azure API key not configured. Set AZURE_OPENAI_API_KEY in environment."

        url = f"{endpoint}/openai/deployments/{deployment}/images/generations?api-version={api_version}"
        
        body = {
            "prompt": prompt,
            "n": 1,
            "size": size,
            "output_format": "png",
            "quality": self.valves.DEFAULT_QUALITY
        }
        
        # Add style if supported
        if style in ("natural", "vivid"):
            body["style"] = style

        try:
            response = requests.post(
                url,
                headers={
                    'Api-Key': api_key,
                    'Content-Type': 'application/json',
                },
                json=body,
                timeout=self.valves.TIMEOUT_SECONDS
            )
            
            if __event_emitter__:
                await __event_emitter__({"type": "status", "data": {"description": "🎨 Processing response...", "done": False}})
            
            if response.status_code == 200:
                data = response.json()
                images = data.get('data', [])
                
                if images and 'b64_json' in images[0]:
                    b64_data = images[0]['b64_json']
                    
                    if __event_emitter__:
                        await __event_emitter__({"type": "status", "data": {"description": "✅ Image generated!", "done": True}})
                    
                    # Return as markdown image with prompt as alt text
                    short_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt
                    return f"![{short_prompt}](data:image/png;base64,{b64_data})\n\n*Generated with FLUX.2-pro ({size})*"
                    
                elif images and 'url' in images[0]:
                    if __event_emitter__:
                        await __event_emitter__({"type": "status", "data": {"description": "✅ Image generated!", "done": True}})
                    return f"![Generated Image]({images[0]['url']})\n\n*Generated with FLUX.2-pro ({size})*"
                else:
                    return f"⚠️ Image generated but no data returned: {data}"
                    
            elif response.status_code == 400:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', response.text)
                # Check for content filter
                if 'content' in error_msg.lower() or 'filter' in error_msg.lower() or 'policy' in error_msg.lower():
                    return f"🚫 Content filtered: The prompt may contain restricted content. Please rephrase.\n\n*Details: {error_msg}*"
                return f"❌ Bad request: {error_msg}\n\nTry rephrasing your prompt or using a different size."
                
            elif response.status_code == 429:
                return "⚠️ Rate limited. Please wait a moment and try again."
                
            else:
                return f"❌ Error {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return "⏱️ Request timed out. Image generation can take up to 3 minutes for complex prompts. Please try again."
        except requests.exceptions.ConnectionError:
            return "❌ Connection error. Please check your network and try again."
        except Exception as e:
            return f"❌ Error generating image: {str(e)}"

    async def generate_image_variations(
        self,
        prompt: str,
        count: int = 2,
        __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Generate multiple image variations from a prompt.
        
        :param prompt: Description of the image to generate
        :param count: Number of variations (2-4)
        :return: Multiple generated images
        """
        if __event_emitter__:
            await __event_emitter__({"type": "status", "data": {"description": f"🎨 Generating {count} variations...", "done": False}})
        
        count = min(max(count, 2), 4)
        results = []
        
        for i in range(count):
            if __event_emitter__:
                await __event_emitter__({"type": "status", "data": {"description": f"🎨 Generating image {i+1}/{count}...", "done": False}})
            
            # Add variation hint to prompt
            varied_prompt = f"{prompt} (variation {i+1})"
            result = await self.generate_image(varied_prompt)
            results.append(f"**Variation {i+1}:**\n{result}")
        
        if __event_emitter__:
            await __event_emitter__({"type": "status", "data": {"description": "✅ All variations generated!", "done": True}})
        
        return "\n\n---\n\n".join(results)

    async def generate_image_options(
        self,
        prompt: str,
        size: str = "",
        __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Generate two different image options from the same prompt for comparison.
        Useful when you want to pick the best result.
        
        :param prompt: Description of the image to generate
        :param size: Image size - 'square', 'landscape', 'portrait', or dimensions like '1024x1024'
        :return: Two generated images side by side for comparison
        """
        import asyncio
        
        if __event_emitter__:
            await __event_emitter__({"type": "status", "data": {"description": "🎨 Generating 2 options...", "done": False}})
        
        # Generate two images in parallel
        async def gen_option(option_num: int):
            if __event_emitter__:
                await __event_emitter__({"type": "status", "data": {"description": f"🎨 Generating option {option_num}...", "done": False}})
            return await self._generate_single_image(prompt, size)
        
        # Run both generations concurrently
        results = await asyncio.gather(gen_option(1), gen_option(2))
        
        if __event_emitter__:
            await __event_emitter__({"type": "status", "data": {"description": "✅ Both options ready!", "done": True}})
        
        output = f"## 🎨 Image Options for: *{prompt[:80]}{'...' if len(prompt) > 80 else ''}*\n\n"
        output += f"### Option A\n{results[0]}\n\n---\n\n### Option B\n{results[1]}"
        return output

    async def _generate_single_image(self, prompt: str, size: str = "") -> str:
        """Internal helper to generate a single image without event emitter."""
        endpoint = self.valves.AZURE_COGNITIVE_ENDPOINT.rstrip('/')
        deployment = self.valves.DEPLOYMENT_NAME
        api_version = self.valves.API_VERSION
        api_key = self.valves.AZURE_API_KEY
        
        # Handle size presets
        if size and size.lower() in self.size_presets:
            size = self.size_presets[size.lower()]
        elif not size:
            size = self.valves.DEFAULT_SIZE

        if not api_key:
            return "❌ Error: Azure API key not configured."

        if not endpoint:
            return "❌ Error: Azure endpoint not configured."

        url = f"{endpoint}/openai/deployments/{deployment}/images/generations?api-version={api_version}"
        
        body = {
            "prompt": prompt,
            "n": 1,
            "size": size,
            "output_format": "png",
            "quality": self.valves.DEFAULT_QUALITY
        }

        try:
            response = requests.post(
                url,
                headers={'Api-Key': api_key, 'Content-Type': 'application/json'},
                json=body,
                timeout=self.valves.TIMEOUT_SECONDS
            )
            
            if response.status_code == 200:
                data = response.json()
                images = data.get('data', [])
                
                if images and 'b64_json' in images[0]:
                    b64_data = images[0]['b64_json']
                    short_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
                    return f"![{short_prompt}](data:image/png;base64,{b64_data})"
                elif images and 'url' in images[0]:
                    return f"![Generated Image]({images[0]['url']})"
                else:
                    return f"⚠️ No image data returned"
            else:
                return f"❌ Error {response.status_code}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
