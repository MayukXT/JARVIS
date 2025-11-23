import os
import logging
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .functions import load_api_key

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

def takeInputGemini(
    inp: str,
    model_name: str = 'gemini-2.0-flash-lite',
    temperature: float = 1.0,
    top_p: float = 0.95,
    top_k: int = 64,
    max_output_tokens: int = 4096,
) -> str:
    """Send a prompt to Google Gemini and return a cleaned response.

    Args:
        inp: User prompt string.
        model_name: Gemini model identifier.
        temperature, top_p, top_k, max_output_tokens: Generation parameters.

    Returns:
        Cleaned response text or an error message.
    """
    api_key = load_api_key()

    attempts = 0
    while attempts < 3:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name)
            
            system_instruction = (
                "You are JARVIS, an AI assistant. "
                "Be concise and short in your replies. "
                "Only provide long, detailed explanations if the user explicitly asks for 'detailed mode' or 'detailed()'. "
            )
            full_prompt = f"{system_instruction}\n\nUser: {inp}"

            response = model.generate_content(
                [full_prompt],
                generation_config={
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "max_output_tokens": max_output_tokens,
                    "response_mime_type": "text/plain",
                },
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                },
            )
            formatted = format_response(str(response.text))
            return formatted
        except Exception as e:
            attempts += 1
            logging.warning(f"Gemini API attempt {attempts} failed: {e}")
            if attempts >= 3:
                return f"Error communicating with Gemini AI after {attempts} attempts: {str(e)}"
            time.sleep(2 ** attempts)  # exponential backoff

def format_response(text: str) -> str:
    """Clean up Gemini response text.
    Removes asterisks, trims whitespace, and ensures a string is returned.
    """
    return text.strip()

def gemini_chat(prompt: str, **kwargs) -> str:
    """Public wrapper for Gemini interaction.
    Accepts a prompt string and optional keyword arguments that map to ``takeInputGemini`` parameters.
    """
    return takeInputGemini(prompt, **kwargs)

def gemini_chat_stream(prompt: str, model_name: str = 'gemini-2.0-flash-lite'):
    """Stream responses from Gemini API.
    
    Args:
        prompt: User prompt string.
        model_name: Gemini model identifier.
        
    Yields:
        Text chunks as they are generated.
    """
    api_key = load_api_key()
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name)
        
        system_instruction = (
            "You are JARVIS, an AI assistant. "
            "Be concise and short in your replies. "
            "Only provide long, detailed explanations if the user explicitly asks for 'detailed mode' or 'detailed()'. "
        )
        full_prompt = f"{system_instruction}\n\nUser: {prompt}"

        response = model.generate_content(
            [full_prompt],
            generation_config={
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 4096,
                "response_mime_type": "text/plain",
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            stream=True,  # Enable streaming
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        logging.error(f"Gemini streaming error: {e}")
        yield f"Error: {str(e)}"

def fn(hello: str) -> str:
    """Simple test function kept for backward compatibility."""
    return f"Hello, {hello}"
