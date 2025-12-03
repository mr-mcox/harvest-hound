client<llm> Anthropic {
  provider anthropic
  options {
    model "claude-sonnet-4-5"
    api_key env.ANTHROPIC_HH_API_KEY
    max_tokens 1024
  }
}
