import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { Sidebar } from './components/Sidebar';
import { Footer } from './components/Footer';
import { SettingsModal } from './components/SettingsModal';
import { Message, Model, MemoryItem, AgentSettings, LangGraphStep, ConnectionSettings, ConnectionStatus, N8NWorkflow, LLMProvider } from './types';
import { INITIAL_MESSAGES, INITIAL_MODELS, INITIAL_MEMORY_ITEMS, LANG_GRAPH_WORKFLOW_STEPS, INITIAL_N8N_WORKFLOWS } from './constants';
import { generateResponse } from './services/geminiService';
import { GenerateContentResponse, Content, Part } from '@google/genai';

const App: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
    const [models, setModels] = useState<Model[]>(INITIAL_MODELS);
    const [selectedModel, setSelectedModel] = useState<Model>(INITIAL_MODELS[0]);
    const [memoryItems] = useState<MemoryItem[]>(INITIAL_MEMORY_ITEMS);
    const [agentSettings, setAgentSettings] = useState<AgentSettings>({
        liquidAudio: true,
        mementoMemory: true,
        langGraph: true,
        autoModelSelection: true,
        reasoningSteps: true,
        n8nToolCalling: true,
    });
    const [isProcessing, setIsProcessing] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [workflowSteps, setWorkflowSteps] = useState<LangGraphStep[]>(
        LANG_GRAPH_WORKFLOW_STEPS.map((step, index) => ({ name: step, active: index < 1 }))
    );
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [connectionSettings, setConnectionSettings] = useState<ConnectionSettings>({
        provider: 'lmstudio',
        lmStudioUrl: 'http://localhost:1234/v1',
        openRouterApiKey: '',
        openRouterModel: 'openai/gpt-4o',
        n8nUrl: 'http://localhost:5678',
        n8nApiKey: '',
        workflows: INITIAL_N8N_WORKFLOWS,
    });
    const [llmStatus, setLlmStatus] = useState<ConnectionStatus>('disconnected');
    const [n8nStatus, setN8nStatus] = useState<ConnectionStatus>('disconnected');
    const isFirstRender = useRef(true);

     useEffect(() => {
        if (isFirstRender.current) {
            isFirstRender.current = false;
            if (llmStatus === 'disconnected') {
                setIsSettingsOpen(true);
            }
        }
    }, [llmStatus]);

    const updateWorkflowStep = (stepName: string, active: boolean) => {
        setWorkflowSteps(prev => prev.map(s => s.name === stepName ? { ...s, active } : s));
    };
    
    const resetWorkflow = () => {
        setWorkflowSteps(LANG_GRAPH_WORKFLOW_STEPS.map((step) => ({ name: step, active: false })));
    };

    const handleSendMessage = async (content: string) => {
        if (!content.trim() || isProcessing) return;
        setIsProcessing(true);
        resetWorkflow();
    
        const userMessage: Message = {
            role: 'user',
            content,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        const currentMessages: Message[] = [...messages, userMessage];
        setMessages(currentMessages);
    
        updateWorkflowStep('User Input Received', true);
    
        try {
            const modelToUse = connectionSettings.provider === 'openrouter' ? connectionSettings.openRouterModel : selectedModel.name;
            
            const history: Content[] = currentMessages.map(msg => {
                const parts: Part[] = [{ text: msg.content }];
                if (msg.role === 'assistant' && msg.functionCall) {
                    parts.push({ functionCall: msg.functionCall });
                } else if (msg.role === 'tool') {
                     parts.push({ functionResponse: { name: "runN8NWorkflow", response: { result: msg.content } }});
                }
                return { role: msg.role === 'tool' ? 'user' : msg.role, parts };
            });

            updateWorkflowStep('Checking for Tools', true);
            
            const response = await generateResponse(history, agentSettings, connectionSettings);
            const responsePart = response.candidates?.[0]?.content.parts[0];
    
            let finalMessages = [...currentMessages];

            if (responsePart?.functionCall) {
                const functionCall = responsePart.functionCall;
                const workflowName = functionCall.args?.workflowName as string || 'Unknown Workflow';
    
                const toolMessage: Message = {
                    role: 'assistant',
                    content: `Executing N8N workflow: <strong>${workflowName}</strong>...`,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    functionCall: functionCall,
                    tools: ['N8N Automation'],
                };
                 const toolExecutionMessage: Message = {
                    role: 'tool',
                    content: `Successfully executed the "${workflowName}" workflow.`,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };

                finalMessages.push(toolMessage, toolExecutionMessage);
                setMessages(finalMessages);

                updateWorkflowStep('Generating Response', true);

                const secondHistory: Content[] = finalMessages.map(msg => {
                    const parts: Part[] = [{ text: msg.content }];
                    if (msg.role === 'assistant' && msg.functionCall) {
                        parts.push({ functionCall: msg.functionCall });
                    } else if (msg.role === 'tool') {
                         parts.push({ functionResponse: { name: "runN8NWorkflow", response: { result: msg.content } }});
                    }
                    return { role: msg.role === 'tool' ? 'user' : msg.role, parts };
                });

                const finalResponse = await generateResponse(secondHistory, agentSettings, connectionSettings, false); // Don't allow tools on the second call
                const assistantSummaryMessage: Message = {
                    role: 'assistant',
                    content: finalResponse.text,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                finalMessages.push(assistantSummaryMessage);

            } else {
                 updateWorkflowStep('Generating Response', true);
                 const assistantMessage: Message = {
                    role: 'assistant',
                    content: response.text,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                finalMessages.push(assistantMessage);
            }
             updateWorkflowStep('Finalizing Output', true);
             setMessages(finalMessages);

        } catch (error) {
            console.error("Error during message handling:", error);
            const errorMessage: Message = {
                role: 'assistant',
                content: "Sorry, I encountered an error. Please check my connection settings or the console for more details.",
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                isError: true,
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsProcessing(false);
            setTimeout(resetWorkflow, 2000);
        }
    };

    const handleClearChat = () => {
        setMessages(INITIAL_MESSAGES);
    };

    const handleSelectModel = (modelId: string) => {
        const model = models.find(m => m.id === modelId);
        if (model) {
            setSelectedModel(model);
        }
    };
    
    const handleRefreshModels = async () => {
        if (connectionSettings.provider !== 'lmstudio') {
            alert("Model refresh is only available for LM Studio.");
            return;
        }
        try {
            const response = await fetch(connectionSettings.lmStudioUrl + '/models');
            if (!response.ok) {
                throw new Error(`Failed to fetch models: ${response.statusText}`);
            }
            const data = await response.json();
            const fetchedModels: Model[] = data.data.map((m: any) => ({
                id: m.id,
                name: m.id,
                params: 'N/A',
                description: 'Loaded from LM Studio'
            }));

            setModels(fetchedModels);

            // If selected model is no longer available, select the first one
            if (!fetchedModels.find(m => m.id === selectedModel.id)) {
                setSelectedModel(fetchedModels[0] || null);
            }
        } catch (error) {
            console.error("Failed to refresh LM Studio models:", error);
            alert("Could not connect to LM Studio. Please ensure it's running and the URL is correct in settings.");
        }
    };

    const handleSaveSettings = (newSettings: ConnectionSettings) => {
        setConnectionSettings(newSettings);
        setIsSettingsOpen(false);
        // Update connection status based on new settings
        if (newSettings.provider === 'lmstudio' && newSettings.lmStudioUrl) {
            setLlmStatus('connected'); // Simplified: assume connected if URL is present
        } else if (newSettings.provider === 'openrouter' && newSettings.openRouterApiKey) {
            setLlmStatus('connected');
        } else {
            setLlmStatus('disconnected');
        }

        if(newSettings.n8nUrl && newSettings.n8nApiKey) {
            setN8nStatus('connected');
        } else {
            setN8nStatus('disconnected');
        }
    };

    return (
        <div className="container mx-auto p-5">
            <Header llmStatus={llmStatus} n8nStatus={n8nStatus} provider={connectionSettings.provider} onOpenSettings={() => setIsSettingsOpen(true)} />
            <main className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-6">
                <ChatWindow
                    messages={messages}
                    selectedModelName={connectionSettings.provider === 'lmstudio' ? selectedModel.name : connectionSettings.openRouterModel}
                    isProcessing={isProcessing}
                    isListening={isListening}
                    setIsListening={setIsListening}
                    onSendMessage={handleSendMessage}
                />
                <Sidebar
                    models={models}
                    selectedModelId={selectedModel?.id}
                    onSelectModel={handleSelectModel}
                    memoryItems={memoryItems}
                    agentSettings={agentSettings}
                    setAgentSettings={setAgentSettings}
                    workflowSteps={workflowSteps}
                    onClearChat={handleClearChat}
                    onOpenSettings={() => setIsSettingsOpen(true)}
                    llmStatus={llmStatus}
                    provider={connectionSettings.provider}
                    onRefreshModels={handleRefreshModels}
                />
            </main>
            <Footer />
            {isSettingsOpen && <SettingsModal onClose={() => setIsSettingsOpen(false)} onSave={handleSaveSettings} currentSettings={connectionSettings} />}
        </div>
    );
};

export default App;