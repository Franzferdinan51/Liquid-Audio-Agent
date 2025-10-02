import { Model, MemoryItem, Message, N8NWorkflow } from './types';

export const INITIAL_MODELS: Model[] = [
    { id: 'llama3', name: 'Llama-3-8B-Instruct', params: '8.03B', description: 'Default' },
    { id: 'mistral', name: 'Mistral-7B-Instruct-v0.3', params: '7.24B', description: 'Fast' },
    { id: 'phi3', name: 'Phi-3-mini-128k-instruct', params: '3.82B', description: 'Long Context' },
    { id: 'gemma2', name: 'Gemma-2-9B-It', params: '9.24B', description: 'Google' },
];

export const INITIAL_MEMORY_ITEMS: MemoryItem[] = [
    { id: 'mem1', title: 'Conversation State', time: '2 min ago', content: 'User prefers audio responses. LangGraph state: active.' },
    { id: 'mem2', title: 'Model Preference', time: '5 min ago', content: 'User selected Llama-3-8B-Instruct for workflows.' },
    { id: 'mem3', title: 'Workflow Context', time: '10 min ago', content: 'Last N8N workflow "Summarize Website" ran successfully.' },
];

export const LANG_GRAPH_WORKFLOW_STEPS: string[] = [
    'User Input Received',
    'Checking for Tools',
    'Generating Response',
    'Finalizing Output',
];

export const INITIAL_N8N_WORKFLOWS: N8NWorkflow[] = [
    { id: '1', name: 'Summarize Website' },
    { id: '2', name: 'Send Daily Digest Email' },
    { id: '3', name: 'Create Calendar Event' },
];

export const INITIAL_MESSAGES: Message[] = [
    {
        role: 'assistant',
        content: `Welcome to your Stateful Liquid Audio Agent! I'm powered by a complete AI stack:<br/><br/>🔥 <strong>LM Studio & OpenRouter</strong> - LLM providers<br/>🧠 <strong>Memento</strong> - Long-term memory & recall<br/>⚡ <strong>LangChain & LangGraph</strong> - Agentic orchestration<br/>🎵 <strong>Liquid Audio</strong> - Voice processing<br/>🤖 <strong>N8N Automation</strong> - Workflow execution via tools<br/><br/>Please configure your LLM Provider and N8N instance in the settings.`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tools: ['LangGraph Workflow', 'N8N Automation'],
        langGraphSteps: LANG_GRAPH_WORKFLOW_STEPS.slice(0, 1).map(name => ({ name, active: true })),
    },
];
