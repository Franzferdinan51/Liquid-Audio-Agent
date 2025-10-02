
import { GoogleGenAI, FunctionDeclaration, Content, Tool, Type, GenerateContentResponse } from "@google/genai";
import { AgentSettings, ConnectionSettings } from "../types";
import { createN8NService } from "./n8nService";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

// Define the function for the model to call
const runN8NWorkflowTool: FunctionDeclaration = {
    name: "runN8NWorkflow",
    description: "Executes a pre-configured N8N workflow to automate a task.",
    parameters: {
        type: Type.OBJECT,
        properties: {
            workflowName: {
                type: Type.STRING,
                description: "The exact name of the workflow to run.",
            },
        },
        required: ["workflowName"],
    },
};

const tools: Tool[] = [{
    functionDeclarations: [runN8NWorkflowTool],
}];

/**
 * Execute N8N workflow when called by the model
 */
export async function executeN8NWorkflow(
  workflowName: string,
  connection: ConnectionSettings
): Promise<string> {
  try {
    const n8nService = createN8NService(connection);
    const result = await n8nService.executeWorkflow(workflowName);

    if (result.success) {
      return `Successfully executed N8N workflow: ${workflowName}${result.executionId ? ` (Execution ID: ${result.executionId})` : ''}`;
    } else {
      return `Failed to execute N8N workflow "${workflowName}": ${result.error}`;
    }
  } catch (error) {
    console.error('Error executing N8N workflow:', error);
    return `Error executing N8N workflow "${workflowName}": ${error instanceof Error ? error.message : 'Unknown error'}`;
  }
}

export async function generateResponse(
  history: Content[],
  settings: AgentSettings,
  connection: ConnectionSettings,
  allowTools: boolean = true,
): Promise<GenerateContentResponse> {

  const modelToUse = connection.provider === 'lmstudio' ? 'gemini-2.5-flash' : connection.openRouterModel;
  const activeSettings = Object.entries(settings)
    .filter(([, value]) => value)
    .map(([key]) => key)
    .join(', ');

  const providerDetails = connection.provider === 'lmstudio'
    ? `You are running via a proxy to Google's Gemini API, but the user believes you are a local model from LM Studio.`
    : `You are running as the model ${connection.openRouterModel} via OpenRouter.`;

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

  try {
    // Fix: systemInstruction and tools should be inside a 'config' object.
    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash', // We use flash for orchestration and logic, regardless of user's selection
        contents: history,
        config: {
            systemInstruction: systemInstruction,
            tools: (allowTools && settings.n8nToolCalling) ? tools : undefined,
        },
    });
    return response;
  } catch (error) {
    console.error("Gemini API call failed:", error);
    throw new Error("Failed to get response from Gemini API.");
  }
}