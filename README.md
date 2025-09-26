# Agentic Code Agent

A powerful coding assistant that executes Python code securely.

## Features
- Execute Python code snippets
- Secure sandboxed execution  
- 30-second timeout protection
- Comprehensive error handling

## API Usage
POST /api/agent
{
  "tool": "executeCode",
  "parameters": {
    "code": "print('Hello World!')",
    "language": "python"
  }
}
