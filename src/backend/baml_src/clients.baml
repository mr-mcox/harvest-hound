client<llm> Anthropic {
  provider anthropic
  options {
    model "claude-sonnet-4-5"
    api_key env.ANTHROPIC_HH_API_KEY
    max_tokens 4096
  }
}

client<llm> AnthropicCreative {
  provider anthropic
  options {
    model "claude-sonnet-4-5"
    api_key env.ANTHROPIC_HH_API_KEY
    max_tokens 4096
    temperature 0.8
  }
}

client<llm> OpenAI {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}
