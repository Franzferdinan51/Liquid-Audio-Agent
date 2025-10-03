import { GenerateContentResponse, FunctionCall, Part } from "@google/genai";
import { AgentSettings, ConnectionSettings, Message } from "../types";

// Define a type for the OpenAI message format
type OpenAIMessage = {
    role: 'system' | 'user' | 'assistant' | 'tool';
    content: string | null;
    tool_calls?: { id: string; type: 'function'; function: { name: string; arguments: string; } }[];
    tool_call_id?: string;
    name?: string;
};

// Define the N8N workflow tool in the OpenAI-compatible format
const runN8NWorkflowToolOpenAI = {
    type: "function",
    function: {
        name: "runN8NWorkflow",
        description: "Executes a pre-configured N8N workflow to automate a task.",
        parameters: {
            type: "object",
            properties: {
                workflowName: {
                    type: "string",
                    description: "The exact name of the workflow to run.",
                },
            },
            required: ["workflowName"],
        },
    }
};
const toolsOpenAI = [runN8NWorkflowToolOpenAI];

function mapMessagesToOpenAI(messages: Message[], systemInstruction: string): OpenAIMessage[] {
    const openAiMessages: OpenAIMessage[] = [{ role: 'system', content: systemInstruction }];

    const filteredMessages = messages.filter(msg => msg.role !== 'system');

    for (const msg of filteredMessages) {
        if (msg.role === 'user') {
            openAiMessages.push({ role: 'user', content: msg.content });
        } else if (msg.role === 'assistant') {
            if (msg.functionCall) {
                openAiMessages.push({
                    role: 'assistant',
                    content: null,
                    tool_calls: [{
                        id: `call_${msg.functionCall.name}_${Date.now()}`,
                        type: 'function',
                        function: {
                            name: msg.functionCall.name,
                            arguments: JSON.stringify(msg.functionCall.args),
                        }
                    }]
                });
            } else {
                openAiMessages.push({ role: 'assistant', content: msg.content });
            }
        } else if (msg.role === 'tool') {
            const lastAssistantMsg = openAiMessages.slice().reverse().find(m => m.role === 'assistant' && !!m.tool_calls);
            if (lastAssistantMsg && lastAssistantMsg.tool_calls) {
                openAiMessages.push({
                    role: 'tool',
                    tool_call_id: lastAssistantMsg.tool_calls[0].id,
                    name: lastAssistantMsg.tool_calls[0].function.name,
                    content: msg.content,
                });
            }
        }
    }
    return openAiMessages;
}

// Helper to transform an OpenAI response back into the app's expected Gemini-like format
function transformOpenAIResponseToGemini(data: any): GenerateContentResponse {
    if (!data || !data.choices || data.choices.length === 0) {
        console.error("LLM response is missing 'choices' array or is malformed. Full response:", data);
        const errorMessage = "Received an empty or invalid response from the LLM.";
        return {
            text: errorMessage,
            // @ts-ignore
            candidates: [{
                content: { role: 'model', parts: [{ text: errorMessage }] }
            }]
        };
    }

    const message = data.choices[0].message;
    if (!message) {
        console.error("LLM response choice is missing 'message' object. Full response:", data);
        const errorMessage = "Received an invalid message structure from the LLM.";
        return {
            text: errorMessage,
            // @ts-ignore
            candidates: [{
                content: { role: 'model', parts: [{ text: errorMessage }] }
            }]
        };
    }
    
    const parts: Part[] = [];
    const responseText = message.content || "";

    if (message.content) {
        parts.push({ text: message.content });
    }

    if (message.tool_calls && message.tool_calls.length > 0) {
        const toolCall = message.tool_calls[0];
        try {
             if (toolCall && toolCall.function && toolCall.function.arguments && toolCall.function.name) {
                const args = JSON.parse(toolCall.function.arguments);
                const functionCall: FunctionCall = {
                    name: toolCall.function.name,
                    args: args,
                };
                parts.push({ functionCall: functionCall });
             } else {
                console.error("Malformed tool_call in LLM response:", toolCall);
                parts.push({ text: "Received a malformed tool call from the LLM." });
             }
        } catch (e) {
            console.error("Failed to parse function call arguments:", e);
            parts.push({ text: "Error processing tool call from LLM." })
        }
    }

    return {
        // @ts-ignore - Mocking the response structure to match what the app expects
        text: responseText,
        candidates: [{
            content: {
                role: 'model',
                parts: parts.length > 0 ? parts : (responseText ? [{ text: responseText }] : [])
            }
        }]
    };
}

export async function generateResponse(
    history: Message[],
    settings: AgentSettings,
    connection: ConnectionSettings,
    modelName: string,
    allowTools: boolean = true,
): Promise<GenerateContentResponse> {

    if (connection.provider !== 'lmstudio' && connection.provider !== 'openrouter') {
        throw new Error(`Unsupported provider: ${connection.provider}. This app is configured for LM Studio or OpenRouter.`);
    }

    const activeSettings = Object.entries(settings)
        .filter(([, value]) => value)
        .map(([key]) => key)
        .join(', ');

    const providerDetails = connection.provider === 'lmstudio'
        ? `You are running as the model ${modelName} locally via LM Studio.`
        : `You are running as the model ${modelName} via OpenRouter.`;

    const systemInstruction = `You are an AI assistant named "Liquid Audio Agent".
Your personality is helpful, concise, and knowledgeable.
You operate within a sophisticated environment that integrates several technologies.
Your core orchestration engine is LangGraph. You must always act as if LangGraph is managing your state and workflow.
The integrated components are:
- LLM Provider: ${providerDetails}
- Liquid Audio: Handles voice input/output.
- Memento: Your long-term memory system. Reference it when discussing context or past interactions.
- LangChain: The foundational agent framework.
- N8N: An automation tool you can use by calling the 'runN8NWorkflow' function. Available workflows are: ${connection.workflows.map(w => w.name).join(', ')}.

Your current settings are: ${activeSettings}.
When responding, acknowledge the workflow. For example: "The LangGraph workflow completed successfully." or "Using Memento for context, I've processed your request."
If you use a tool, your final response should summarize the result of the tool's action. Do not output the raw tool result.
`;

    const url = connection.provider === 'lmstudio'
        ? connection.lmStudioUrl.replace(/\/v1\/?$/, '') + '/v1/chat/completions'
        : 'https://openrouter.ai/api/v1/chat/completions';

    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (connection.provider === 'openrouter') {
        headers['Authorization'] = `Bearer ${connection.openRouterApiKey}`;
    }

    const messages = mapMessagesToOpenAI(history, systemInstruction);
    const body: any = { model: modelName, messages: messages };

    if (allowTools && settings.n8nToolCalling) {
        body.tools = toolsOpenAI;
        body.tool_choice = 'auto';
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorBody = await response.text();
            console.error(`API call failed to ${connection.provider}:`, response.status, errorBody);
            throw new Error(`Failed to get response from ${connection.provider}. Status: ${response.status}.`);
        }

        const data = await response.json();
        return transformOpenAIResponseToGemini(data);
    } catch (error) {
        console.error(`Error calling ${connection.provider} API:`, error);
        throw new Error(`Failed to get response from ${connection.provider}. Check console for details.`);
    }
}