import json
from app.security import decrypt_secret

def create_llm_instance(profile_data: dict):
    provider = profile_data.get("provider", "").lower()
    model = profile_data.get("model", "")
    decrypted_key = decrypt_secret(profile_data.get("api_key_enc", ""))
    base_url = profile_data.get("base_url")
    temperature = profile_data.get("temperature", 0.7)
    extra_params = json.loads(profile_data.get("extra_params") or "{}")

    if provider in ("chatbrowseruse", "browser-use", "browseruse"):
        from browser_use import ChatBrowserUse
        return ChatBrowserUse(
            api_key=decrypted_key,
            temperature=temperature,
            **extra_params
        )

    elif provider in ("chatopenai", "openai", "custom-openai", "custom"):
        from langchain_openai import ChatOpenAI
        kwargs = {
            "model": model or "gpt-4o",
            "api_key": decrypted_key,
            "temperature": temperature,
            **extra_params
        }
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)

    elif provider in ("chatanthropic", "anthropic"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            api_key=decrypted_key,
            temperature=temperature,
            **extra_params
        )

    elif provider in ("chatgroq", "groq"):
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model or "llama-3.3-70b-versatile",
            api_key=decrypted_key,
            temperature=temperature,
            **extra_params
        )

    elif provider in ("chatollama", "ollama"):
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model or "llama3.1",
            base_url=base_url or "http://localhost:11434",
            temperature=temperature,
            **extra_params
        )

    elif provider in ("chatdeepseek", "deepseek"):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "deepseek-chat",
            api_key=decrypted_key,
            base_url=base_url or "https://api.deepseek.com/v1",
            temperature=temperature,
            **extra_params
        )

    else:
        from langchain_openai import ChatOpenAI
        kwargs = {
            "model": model or "gpt-4o-mini",
            "api_key": decrypted_key,
            "temperature": temperature,
            **extra_params
        }
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)
