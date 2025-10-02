import { FunctionCall } from "@google/genai";

export interface LangGraphStep {
    name: string;
    active: boolean;
}

export interface Message {
    role: 'user' | 'assistant' | 'tool';
    content: string;
    time: string;
    tools?: string[];
    langGraphSteps?: LangGraphStep[];
    functionCall?: FunctionCall;
    isError?: boolean;
}

export interface Model {
    id: string;
    name: string;
    params: string;
    description: string;
}

export interface MemoryItem {
    id: string;
    title: string;
    time: string;
    content: string;
}

export interface AgentSettings {
    liquidAudio: boolean;
    mementoMemory: boolean;
    langGraph: boolean;
    autoModelSelection: boolean;
    reasoningSteps: boolean;
    n8nToolCalling: boolean;
}

export interface N8NWorkflow {
    id: string;
    name: string;
}

export type LLMProvider = 'lmstudio' | 'openrouter';
export type ConnectionStatus = 'connected' | 'disconnected';

export interface ConnectionSettings {
    provider: LLMProvider;
    lmStudioUrl: string;
    openRouterApiKey: string;
    openRouterModel: string;
    n8nUrl: string;
    n8nApiKey: string;
    workflows: N8NWorkflow[];
}