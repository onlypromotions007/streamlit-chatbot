[![CraigDoesData][logo]][link]

[logo]: https://github.com/thecraigd/Python_SQL/raw/master/img/logo.png
[link]: https://www.craigdoesdata.com/

# AI Chatbot

A versatile AI conversation platform supporting multiple providers 
including Google Gemini 2.0 Flash Thinking, Deepseek r1, Deepseek Chat, OpenAI 
GPT-4o, and Anthropic Claude.

## Features

- **Multi-Provider Support**: Access different AI models through various 
providers.
- **Temperature Control**: Adjust the randomness of responses (default: 
0.7).
- **API Key Management**: Centralized API key input with validation.
- **Responsive Design**: Clean and modern interface for seamless 
interaction.
- **Error Handling**: Clear display of any encountered errors.

## Configuration

### Step 1: Choose Your Provider
Select from the dropdown menu below to switch between supported AI 
providers:

```
Provider Selection:
OpenAI GPT-4o
Deepseek r1
Deepseek Chat
OpenAI GPT-4o
```

### Step 2: Set API Key (Optional)
Enter your API key for OpenAI and Anthropic directly in the sidebar or use 
the `secrets` module:

```
API Key:
[Enter your API key here]
```

### Step 3: Adjust Temperature (Optional)
Fine-tune AI responses with this slider:

```
Temperature:
[Slider from 0.0 to 2.0, default: 0.7]
```

## How It Works

1. **Input Your Message**: Start typing your message in the chat input 
box.
2. **Select Provider (Optional)**: Choose which AI provider you want 
to use for generating responses.
3. **Generate Response**: Click "Enter" or click the "AI Assistant" button 
below.

## API Reference

### Google Gemini 2.0 Flash Thinking
```python
response = generate_response(messages, api_key, "Google Gemini 2.0 Flash Thinking", 
temperature)
```

### Deepseek r1 and Deepseek Chat
```python
response = generate_response(messages, api_key, "Deepseek [Your Model]", 
temperature)
```

### OpenAI GPT-4o
```python
response = generate_response(messages, api_key, "OpenAI GPT-4o", 
temperature)
```

### Anthropic Claude
```python
response = generate_response(messages, api_key, "Anthropic Claude", 
temperature)
```

## Customization

1. **Change Theme**: Toggle between light and dark themes using the 
provided buttons.
2. **Add More Providers**: Extend the code to include additional providers 
as needed.

## Error Handling

In case of any errors:
- Display error messages in the chat interface
- Highlight invalid API key inputs if applicable

## Security Considerations

- Always ensure your API keys are kept secure and not exposed publicly
- Implement rate limiting for API calls based on usage patterns
- Use environment variables for storing sensitive API keys

## Contributing

1. Fork the repository
2. Create a `.gitignore` file to exclude unnecessary files
3. Add new features or themes using your brand colors
