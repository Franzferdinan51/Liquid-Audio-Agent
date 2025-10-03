import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { Sidebar } from './components/Sidebar';
import { Footer } from './components/Footer';
import { SettingsModal } from './components/SettingsModal';
import { Message, Model, MemoryItem, AgentSettings, LangGraphStep, ConnectionSettings, ConnectionStatus, N8NWorkflow, LLMProvider } from './types';
import { INITIAL_MESSAGES, INITIAL_MODELS, INITIAL_MEMORY_ITEMS, LANG_GRAPH_WORKFLOW_STEPS, INITIAL_N8N_WORKFLOWS } from './constants';
import { generateResponse } from './services/geminiService';
import { textToSpeech } from './services/liquidAudioService';

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
    const [isAssistantSpeaking, setIsAssistantSpeaking] = useState(false);
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
        liquidAudioUrl: 'http://localhost:8081/v1/audio/speech',
        webhookUrl: '',
    });
    const [llmStatus, setLlmStatus] = useState<ConnectionStatus>('disconnected');
    const [n8nStatus, setN8nStatus] = useState<ConnectionStatus>('disconnected');
    const [liquidAudioStatus, setLiquidAudioStatus] = useState<ConnectionStatus>('disconnected');
    const [webhookStatus, setWebhookStatus] = useState<ConnectionStatus>('disconnected');
    const isFirstRender = useRef(true);
    const audioContextRef = useRef<AudioContext | null>(null);
    const webhookIntervalRef = useRef<number | null>(null);
    const lastWebhookRequestRef = useRef<string | null>(null);

     useEffect(() => {
        if (isFirstRender.current) {
            isFirstRender.current = false;
            if (llmStatus === 'disconnected') {
                setIsSettingsOpen(true);
            }
        }
    }, [llmStatus]);

    useEffect(() => {
        // Initialize AudioContext after a user gesture (e.g., component mount)
        // to comply with browser autoplay policies.
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }, []);

    useEffect(() => {
        if (webhookStatus === 'connected' && connectionSettings.webhookUrl) {
            const url = connectionSettings.webhookUrl;
            const match = url.match(/webhook\.site\/(?:#!\/(?:view\/)?)?([a-f0-9-]+)/);

            if (match && match[1]) {
                const token = match[1];
                const apiUrl = `https://webhook.site/token/${token}/requests?sorting=newest`;

                const poll = async () => {
                    try {
                        const response = await fetch(apiUrl, { headers: { 'Accept': 'application/json' } });
                        if (!response.ok) {
                            console.error('Failed to poll webhook, disconnecting.');
                            setWebhookStatus('disconnected');
                            if(webhookIntervalRef.current) clearInterval(webhookIntervalRef.current);
                            return;
                        }
                        const data = await response.json();
                        if (data.data && data.data.length > 0) {
                            const latestRequest = data.data[0];
                            if (latestRequest.uuid !== lastWebhookRequestRef.current) {
                                if (lastWebhookRequestRef.current !== null) { 
                                    let content = 'Received non-JSON data from N8N Webhook.';
                                    try {
                                        const parsedContent = JSON.parse(latestRequest.content);
                                        content = `Received data from N8N Webhook: <pre class="whitespace-pre-wrap text-left text-xs bg-black/30 p-3 rounded-md mt-2">${JSON.stringify(parsedContent, null, 2)}</pre>`;
                                    } catch (e) {
                                        content = `Received data from N8N Webhook: <pre class="whitespace-pre-wrap text-left text-xs bg-black/30 p-3 rounded-md mt-2">${latestRequest.content}</pre>`;
                                    }
                                    
                                    const webhookMessage: Message = {
                                        role: 'system',
                                        content: content,
                                        time: new Date(latestRequest.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                                    };
                                    setMessages(prev => [...prev, webhookMessage]);
                                }
                                lastWebhookRequestRef.current = latestRequest.uuid;
                            }
                        }
                    } catch (error) {
                        console.error('Error polling webhook:', error);
                        setWebhookStatus('disconnected');
                        if(webhookIntervalRef.current) clearInterval(webhookIntervalRef.current);
                    }
                };
                
                const initLastRequest = async () => {
                    try {
                        const response = await fetch(apiUrl, { headers: { 'Accept': 'application/json' } });
                        const data = await response.json();
                        if (data.data && data.data.length > 0) {
                            lastWebhookRequestRef.current = data.data[0].uuid;
                        }
                        webhookIntervalRef.current = window.setInterval(poll, 5000);
                    } catch (e) {
                        console.error("Failed to initialize webhook listener", e);
                        setWebhookStatus('disconnected');
                    }
                }
                initLastRequest();
            } else {
                 setWebhookStatus('disconnected');
            }
        }

        return () => {
            if (webhookIntervalRef.current) {
                clearInterval(webhookIntervalRef.current);
                webhookIntervalRef.current = null;
            }
        };
    }, [webhookStatus, connectionSettings.webhookUrl]);

    const playAudio = (audioData: ArrayBuffer) => {
        if (!audioContextRef.current) return;
        setIsAssistantSpeaking(true);
        audioContextRef.current.decodeAudioData(audioData, (buffer) => {
            const source = audioContextRef.current!.createBufferSource();
            source.buffer = buffer;
            source.connect(audioContextRef.current!.destination);
            source.start(0);
            source.onended = () => {
                setIsAssistantSpeaking(false);
            };
        }, (error) => {
            console.error('Error decoding audio data:', error);
            setIsAssistantSpeaking(false);
        });
    };

    const updateWorkflowStep = (stepName: string, active: boolean) => {
        setWorkflowSteps(prev => prev.map(s => s.name === stepName ? { ...s, active } : s));
    };
    
    const resetWorkflow = () => {
        setWorkflowSteps(LANG_GRAPH_WORKFLOW_STEPS.map((step) => ({ name: step, active: false })));
    };

    const handleSendMessage = async (content: string, isFromVoice: boolean = false) => {
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
            updateWorkflowStep('Checking for Tools', true);
            
            const modelName = connectionSettings.provider === 'lmstudio' 
                ? selectedModel.name 
                : connectionSettings.openRouterModel;

            let finalMessages = [...currentMessages];

            const processResponse = async (history: Message[], allowTools = true) => {
                const response = await generateResponse(history, agentSettings, connectionSettings, modelName, allowTools);
                const responsePart = response.candidates?.[0]?.content.parts[0];

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

                    // Recursive call to get the final summary
                    return await processResponse(finalMessages, false);
                }
                updateWorkflowStep('Generating Response', true);
                return response.text;
            };

            const assistantText = await processResponse(finalMessages);
            
            const assistantMessage: Message = {
                role: 'assistant',
                content: assistantText,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };
            finalMessages.push(assistantMessage);

             updateWorkflowStep('Finalizing Output', true);
             setMessages(finalMessages);

             if (isFromVoice && agentSettings.liquidAudio && connectionSettings.liquidAudioUrl) {
                try {
                    const audioData = await textToSpeech(assistantText, connectionSettings.liquidAudioUrl);
                    playAudio(audioData);
                } catch (error) {
                    console.error("Failed to generate or play audio:", error);
                    const errorMessage: Message = {
                        role: 'assistant',
                        content: "Sorry, I couldn't generate an audio response.",
                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                        isError: true,
                    };
                    setMessages(prev => [...prev, errorMessage]);
                }
            }

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

        if (newSettings.provider === 'lmstudio' && newSettings.lmStudioUrl) {
            setLlmStatus('connected');
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

        if (newSettings.liquidAudioUrl) {
            setLiquidAudioStatus('connected');
        } else {
            setLiquidAudioStatus('disconnected');
        }

        if (newSettings.webhookUrl) {
            setWebhookStatus('connected');
        } else {
            setWebhookStatus('disconnected');
        }
    };

    return (
        <div className="container mx-auto p-5">
            <Header llmStatus={llmStatus} n8nStatus={n8nStatus} liquidAudioStatus={liquidAudioStatus} webhookStatus={webhookStatus} provider={connectionSettings.provider} onOpenSettings={() => setIsSettingsOpen(true)} />
            <main className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-6">
                <ChatWindow
                    messages={messages}
                    selectedModelName={connectionSettings.provider === 'lmstudio' ? selectedModel.name : connectionSettings.openRouterModel}
                    isProcessing={isProcessing}
                    isListening={isListening}
                    setIsListening={setIsListening}
                    isAssistantSpeaking={isAssistantSpeaking}
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
