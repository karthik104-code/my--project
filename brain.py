import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools.system_tools import get_current_time, open_application, compose_email, save_note, create_calendar_event

load_dotenv()

# Initialize OpenAI client pointing to local Ollama instance
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key=os.getenv("OLLAMA_API_KEY", "7b355c2f2ff44811b0ae3ba1a1cff08d.gsQQmagpe7NM5c7lF3zPARmd"),
)

model_name = os.getenv("OLLAMA_MODEL", "llama3.2")

available_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current local date and time.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Opens a common Windows application by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to open (e.g., 'notepad', 'calculator', 'cmd', 'explorer', 'browser')"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compose_email",
            "description": "Opens the default email client (Gmail in browser) to draft an email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_address": {"type": "string", "description": "The recipient's email address"},
                    "subject": {"type": "string", "description": "The email subject"},
                    "body": {"type": "string", "description": "The email body"}
                },
                "required": ["to_address", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Saves a textual note or reminder to a text file and automatically opens it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "A short, safe filename for the note (without extension)."},
                    "content": {"type": "string", "description": "The full text content to save."}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Creates a calendar event file and opens it in the user's default calendar application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title or summary of the event"},
                    "date_YYYYMMDD": {"type": "string", "description": "The date of the event in exactly YYYYMMDD format (e.g. 20261225). Use current system time context to deduce this."},
                    "time_HHMMSS": {"type": "string", "description": "The time of the event in exactly HHMMSS format (e.g. 143000 for 2:30 PM)."}
                },
                "required": ["title", "date_YYYYMMDD", "time_HHMMSS"]
            }
        }
    }
]

system_prompt = (
    "You are Commander, a highly capable desktop AI assistant. "
    "You have access to tools to perform tasks for the user on their computer. "
    "CRITICAL INSTRUCTION: If a user asks you to perform a task but does not provide "
    "all the necessary information (e.g., they say 'send an email' but don't specify who to, "
    "the subject, or the body), DO NOT guess the information and DO NOT execute the tool yet. "
    "Instead, ask the user a brief follow-up question to get the missing details. "
    "CRITICAL EMAIL RULE: Before calling the `compose_email` tool, you MUST explicitly repeat back the email address and ask the user to confirm the exact spelling (e.g. 'You want to send to john.doe@example.com, is that spelled correctly?'). Wait for them to say yes or provide the correct spelling before executing the tool! "
    "Keep your text responses conversational but brief (1-3 sentences) as they will be spoken aloud by a Text-To-Speech engine."
)

chat_history = [
    {"role": "system", "content": system_prompt}
]

def process_command(user_text: str) -> str:
    global chat_history
    
    print(f"Brain received: '{user_text}'")
    current_time_str = get_current_time()
    chat_history.append({"role": "system", "content": f"Context: The current system time is {current_time_str}. Use this to determine dates/times for calendar events if relative times like 'tomorrow' are used."})
    chat_history.append({"role": "user", "content": user_text})
    
    try:
        # Send to Ollama
        response = client.chat.completions.create(
            model=model_name,
            messages=chat_history,
            tools=available_tools,
            temperature=0.2
        )
        
        reply = response.choices[0].message
        chat_history.append(reply)
        
        # Process tool calls
        while getattr(reply, "tool_calls", None):
            for tool_call in reply.tool_calls:
                func_name = tool_call.function.name
                
                # Extract args securely
                try:
                    args_dict = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                except Exception:
                    args_dict = {}
                    
                print(f"Executing tool: {func_name}({args_dict})")
                
                # Execute the matched tool
                if func_name == "get_current_time":
                    result = get_current_time()
                elif func_name == "open_application":
                    result = open_application(args_dict.get("app_name", ""))
                elif func_name == "compose_email":
                    result = compose_email(
                        to_address=args_dict.get("to_address", ""),
                        subject=args_dict.get("subject", ""),
                        body=args_dict.get("body", "")
                    )
                elif func_name == "save_note":
                    result = save_note(
                        filename=args_dict.get("filename", "note"),
                        content=args_dict.get("content", "")
                    )
                elif func_name == "create_calendar_event":
                    result = create_calendar_event(
                        title=args_dict.get("title", ""),
                        date_YYYYMMDD=args_dict.get("date_YYYYMMDD", ""),
                        time_HHMMSS=args_dict.get("time_HHMMSS", "")
                    )
                else:
                    result = f"Error: Tool {func_name} not found."
                    
                print(f"Tool Result: {result}")
                
                # Append result to history
                chat_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": str(result)
                })
                
            # Request next iteration from Ollama
            response = client.chat.completions.create(
                model=model_name,
                messages=chat_history,
                tools=available_tools,
                temperature=0.2
            )
            reply = response.choices[0].message
            chat_history.append(reply)
                
        # Return final textual answer
        content = reply.content
        if not content:
            content = "Task executed."
        return content
            
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"Error in brain processing:\n{err_msg}")
        return "I encountered an error understanding your command. Please check if Ollama is running."
