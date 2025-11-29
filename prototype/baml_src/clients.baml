client<llm> GPT41Mini {
  provider openai
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
  }
}
client<llm> Anthropic {
  provider anthropic
  options {
    model "claude-sonnet-4-5"
    api_key env.ANTHROPIC_HH_API_KEY
    max_tokens 4096
    thinking {
      type "enabled"
      budget_tokens 2000
    }
  }
}
