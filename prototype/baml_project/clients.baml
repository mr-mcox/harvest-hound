client<llm> GPT41Mini {
  provider openai
  options {
    model "gpt-4.1-mini"
    api_key env.OPENAI_API_KEY
  }
}
