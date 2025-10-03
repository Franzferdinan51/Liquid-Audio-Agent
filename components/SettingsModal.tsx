import React, { useState } from 'react';
import { ConnectionSettings, LLMProvider, N8NWorkflow } from '../types';

interface SettingsModalProps {
    onClose: () => void;
    onSave: (settings: ConnectionSettings) => void;
    currentSettings: ConnectionSettings;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ onClose, onSave, currentSettings }) => {
    const [settings, setSettings] = useState<ConnectionSettings>(currentSettings);
    const [llmTestStatus, setLlmTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
    const [n8nTestStatus, setN8nTestStatus] = useState<'idle' | 'testing' | 'success' | { error: string }>('idle');
    const [liquidAudioTestStatus, setLiquidAudioTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
    const [manualWorkflows, setManualWorkflows] = useState('');

    const handleProviderChange = (provider: LLMProvider) => {
        setSettings(prev => ({ ...prev, provider }));
    };

    const handleSave = () => {
        onSave(settings);
    };

    const handleTestLlmConnection = () => {
        setLlmTestStatus('testing');
        // This is a simplified test. A real implementation would make an API call.
        setTimeout(() => {
            if (settings.provider === 'lmstudio' && settings.lmStudioUrl.includes('localhost')) {
                setLlmTestStatus('success');
            } else if (settings.provider === 'openrouter' && settings.openRouterApiKey.startsWith('sk-or-')) {
                 setLlmTestStatus('success');
            } else {
                setLlmTestStatus('error');
            }
            setTimeout(() => setLlmTestStatus('idle'), 2000);
        }, 1500);
    };

    const handleTestLiquidAudioConnection = () => {
        setLiquidAudioTestStatus('testing');
        setTimeout(() => {
            if (settings.liquidAudioUrl) {
                setLiquidAudioTestStatus('success');
            } else {
                setLiquidAudioTestStatus('error');
            }
            setTimeout(() => setLiquidAudioTestStatus('idle'), 2000);
        }, 1500);
    };

    const handleFetchWorkflows = async () => {
        setN8nTestStatus('testing');
        try {
            const response = await fetch(`${settings.n8nUrl}/api/v1/workflows`, {
                headers: {
                    'X-N8N-API-KEY': settings.n8nApiKey,
                },
            });
            if (!response.ok) {
                 if(response.status === 401) {
                    throw new Error(`Authorization failed. Please check your N8N API Key.`);
                }
                throw new Error(`N8N API responded with status ${response.status}`);
            }
            const data = await response.json();
            const fetchedWorkflows: N8NWorkflow[] = data.data.map((wf: any) => ({
                id: wf.id,
                name: wf.name,
            }));
            setSettings(s => ({ ...s, workflows: fetchedWorkflows }));
            setN8nTestStatus('success');
            setTimeout(() => setN8nTestStatus('idle'), 2000);
        } catch (error) {
            console.error("Failed to fetch N8N workflows:", error);
            let errorMessage = "An unknown error occurred.";
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                errorMessage = "CORS Policy Error. Your browser blocked the request. Ensure your N8N instance is configured to allow requests from this origin. See note below for help.";
            } else if (error instanceof Error) {
                errorMessage = error.message;
            }
            setN8nTestStatus({ error: errorMessage });
        }
    };
    
    const handleSaveManualWorkflows = () => {
        const workflowNames = manualWorkflows.split('\n').map(name => name.trim()).filter(name => name);
        const newWorkflows: N8NWorkflow[] = workflowNames.map((name, index) => ({
            id: `manual-${index}-${Date.now()}`,
            name: name,
        }));
        setSettings(s => ({ ...s, workflows: newWorkflows }));
        setManualWorkflows('');
        setN8nTestStatus('success');
        setTimeout(() => setN8nTestStatus('idle'), 2000);
    };

    const handleGenerateWebhook = () => {
        const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
        setSettings(s => ({ ...s, webhookUrl: `https://webhook.site/${uuid}` }));
    };

    const renderTestButton = (status: 'idle' | 'testing' | 'success' | 'error' | { error: string }) => {
        switch (status) {
            case 'testing':
                return <div className="w-5 h-5 border-2 border-white/30 border-t-amber-500 rounded-full animate-spin"></div>;
            case 'success':
                return <i className="fas fa-check-circle text-emerald-400"></i>;
            case 'error':
                 return <i className="fas fa-times-circle text-red-400"></i>;
            default:
                if (typeof status === 'object' && status.error) {
                    return <i className="fas fa-times-circle text-red-400"></i>;
                }
                return null;
        }
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50">
            <div className="bg-stone-900 border border-white/10 rounded-2xl w-full max-w-xl shadow-2xl">
                <div className="p-6 border-b border-white/10 flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-red-200 flex items-center gap-3"><i className="fas fa-cogs"></i>Agent Settings</h2>
                    <button onClick={onClose} className="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center">
                        <i className="fas fa-times"></i>
                    </button>
                </div>
                <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                    {/* LLM Provider Section */}
                    <div className="p-4 bg-black/20 rounded-lg space-y-4 border border-white/10">
                        <h3 className="font-semibold text-amber-300 text-lg">LLM Provider</h3>
                        <div className="flex gap-2 bg-black/40 p-1 rounded-lg">
                            <button onClick={() => handleProviderChange('lmstudio')} className={`flex-1 p-2 rounded-md text-sm font-semibold transition-colors ${settings.provider === 'lmstudio' ? 'bg-red-600 text-white' : 'hover:bg-white/5'}`}>
                                LM Studio
                            </button>
                            <button onClick={() => handleProviderChange('openrouter')} className={`flex-1 p-2 rounded-md text-sm font-semibold transition-colors ${settings.provider === 'openrouter' ? 'bg-red-600 text-white' : 'hover:bg-white/5'}`}>
                                OpenRouter
                            </button>
                        </div>
                        {settings.provider === 'lmstudio' && (
                             <div>
                                <label htmlFor="lmStudioUrl" className="block text-sm font-medium text-gray-300 mb-2">Server URL</label>
                                <div className="relative">
                                    <input type="text" id="lmStudioUrl" value={settings.lmStudioUrl} onChange={e => setSettings(s => ({ ...s, lmStudioUrl: e.target.value }))} className="w-full bg-black/40 border border-white/20 rounded-lg p-2.5 pr-24 focus:border-red-500 outline-none" placeholder="http://localhost:1234/v1" />
                                    <button onClick={handleTestLlmConnection} className="absolute right-1 top-1 bottom-1 px-3 bg-white/10 rounded-md hover:bg-white/20 text-xs font-semibold flex items-center gap-2">
                                        Test {renderTestButton(llmTestStatus)}
                                    </button>
                                </div>
                            </div>
                        )}
                        {settings.provider === 'openrouter' && (
                            <div className="space-y-4">
                                <div>
                                    <label htmlFor="apiKey" className="block text-sm font-medium text-gray-300 mb-2">API Key</label>
                                    <input type="password" id="apiKey" value={settings.openRouterApiKey} onChange={e => setSettings(s => ({ ...s, openRouterApiKey: e.target.value }))} className="w-full bg-black/40 border border-white/20 rounded-lg p-2.5 focus:border-red-500 outline-none" placeholder="sk-or-..." />
                                </div>
                                 <div>
                                    <label htmlFor="modelName" className="block text-sm font-medium text-gray-300 mb-2">Model Name</label>
                                    <input type="text" id="modelName" value={settings.openRouterModel} onChange={e => setSettings(s => ({ ...s, openRouterModel: e.target.value }))} className="w-full bg-black/40 border border-white/20 rounded-lg p-2.5 focus:border-red-500 outline-none" placeholder="openai/gpt-4o" />
                                </div>
                            </div>
                        )}
                    </div>
                    {/* Liquid Audio Section */}
                    <div className="p-4 bg-black/20 rounded-lg space-y-4 border border-white/10">
                        <h3 className="font-semibold text-red-300 text-lg">Liquid Audio</h3>
                        <div>
                            <label htmlFor="liquidAudioUrl" className="block text-sm font-medium text-gray-300 mb-2">llama.cpp Server URL</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    id="liquidAudioUrl"
                                    value={settings.liquidAudioUrl}
                                    onChange={e => setSettings(s => ({ ...s, liquidAudioUrl: e.target.value }))}
                                    className="w-full bg-black/40 border border-white/20 rounded-lg p-2.5 pr-24 focus:border-red-500 outline-none"
                                    placeholder="http://localhost:8081/v1/audio/speech"
                                />
                                <button onClick={handleTestLiquidAudioConnection} className="absolute right-1 top-1 bottom-1 px-3 bg-white/10 rounded-md hover:bg-white/20 text-xs font-semibold flex items-center gap-2">
                                    Test {renderTestButton(liquidAudioTestStatus)}
                                </button>
                            </div>
                        </div>
                        <div className="text-xs text-gray-400 mt-2 p-2 bg-black/30 rounded-md">
                            <i className="fas fa-info-circle mr-1.5"></i>
                            Required for local voice generation. Point this to your llama.cpp server's TTS endpoint.
                        </div>
                    </div>
                    {/* N8N Automation Section */}
                    <div className="p-4 bg-black/20 rounded-lg space-y-4 border border-white/10">
                        <h3 className="font-semibold text-sky-300 text-lg">N8N Automation</h3>
                         <div>
                            <label htmlFor="n8nUrl" className="block text-sm font-medium text-gray-300 mb-2">N8N URL</label>
                            <input type="text" id="n8nUrl" value={settings.n8nUrl} onChange={e => setSettings(s => ({ ...s, n8nUrl: e.target.value }))} className="w-full bg-black/40 border border-white/20 rounded-lg p-2.5 focus:border-sky-500 outline-none" placeholder="http://localhost:5678" />
                        </div>
                         <div>
                            <label htmlFor="n8nApiKey" className="block text-sm font-medium text-gray-300 mb-2">API Key</label>
                            <div className="relative">
                                 <input type="password" id="n8nApiKey" value={settings.n8nApiKey} onChange={e => setSettings(s => ({ ...s, n8nApiKey: e.target.value }))} className="w-full bg-black/40 border border-white/20 rounded-lg p-2.5 pr-36 focus:border-sky-500 outline-none" placeholder="Enter your N8N API Key" />
                                <button onClick={handleFetchWorkflows} className="absolute right-1 top-1 bottom-1 px-3 bg-white/10 rounded-md hover:bg-white/20 text-xs font-semibold flex items-center gap-2">
                                    Test & Fetch {renderTestButton(n8nTestStatus)}
                                </button>
                            </div>
                        </div>
                         {typeof n8nTestStatus === 'object' && n8nTestStatus.error && (
                             <>
                                <div className="text-xs text-red-300 p-3 bg-red-500/10 rounded-md mt-2 border border-red-500/20">
                                    <strong>Connection Failed:</strong> {n8nTestStatus.error}
                                    <br/><br/>
                                    This is likely a CORS issue. Please see the note at the bottom of this section on how to configure your N8N server.
                                    <br/>
                                    <strong>As an alternative, you can add your workflows manually below.</strong>
                                </div>
                                <div className="mt-4">
                                    <label htmlFor="manualWorkflows" className="block text-sm font-medium text-gray-300 mb-2">Manual Workflow Entry</label>
                                    <textarea
                                        id="manualWorkflows"
                                        value={manualWorkflows}
                                        onChange={e => setManualWorkflows(e.target.value)}
                                        className="w-full h-24 bg-black/40 border border-white/20 rounded-lg p-2.5 focus:border-sky-500 outline-none"
                                        placeholder="Enter one workflow name per line..."
                                    />
                                    <button onClick={handleSaveManualWorkflows} className="mt-2 w-full px-3 py-2 bg-sky-600/50 rounded-md hover:bg-sky-600/70 text-xs font-semibold text-white">
                                        Save Manual Workflows
                                    </button>
                                </div>
                            </>
                        )}
                        {settings.workflows.length > 0 && (
                            <div>
                                <h4 className="text-sm font-medium text-gray-300 mb-2">Fetched Workflows:</h4>
                                <div className="flex flex-wrap gap-2">
                                    {settings.workflows.map(wf => (
                                        <span key={wf.id} className="bg-sky-500/10 text-sky-300 px-2 py-1 rounded text-xs border border-sky-500/20">{wf.name}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        <div className="text-xs text-gray-400 mt-2 p-2 bg-black/30 rounded-md">
                            <i className="fas fa-info-circle mr-1.5"></i>
                            <strong>Note:</strong> For this to work, your N8N instance must have CORS configured. You can do this by setting the environment variable 
                            <code className="bg-stone-700 p-1 rounded mx-1 text-white text-[11px]">N8N_CORS_ALLOW_ORIGIN=*</code> on your N8N server.
                        </div>
                    </div>

                    {/* N8N Webhook Section */}
                    <div className="p-4 bg-black/20 rounded-lg space-y-4 border border-white/10">
                        <h3 className="font-semibold text-purple-300 text-lg">N8N Webhook Listener</h3>
                        <div>
                            <label htmlFor="webhookUrl" className="block text-sm font-medium text-gray-300 mb-2">Webhook URL</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    id="webhookUrl"
                                    value={settings.webhookUrl}
                                    onChange={e => setSettings(s => ({ ...s, webhookUrl: e.target.value }))}
                                    className="w-full bg-black/40 border border-white/20 rounded-lg p-2.5 focus:border-purple-500 outline-none"
                                    placeholder="Generate or paste a webhook.site URL"
                                />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                            <button onClick={handleGenerateWebhook} className="w-full px-3 py-2 bg-purple-600/50 rounded-md hover:bg-purple-600/70 text-xs font-semibold text-white">
                                Generate New URL
                            </button>
                            <button onClick={() => navigator.clipboard.writeText(settings.webhookUrl)} disabled={!settings.webhookUrl} className="w-full px-3 py-2 bg-white/10 rounded-md hover:bg-white/20 text-xs font-semibold text-white disabled:opacity-50">
                                Copy URL
                            </button>
                        </div>
                        {settings.webhookUrl.includes('webhook.site') && (
                            <a href={settings.webhookUrl.replace(/webhook.site\/(.*)/, "https://webhook.site/#!/view/$1")} target="_blank" rel="noopener noreferrer" className="text-xs text-purple-300 hover:underline text-center block">
                                Open inspector in new tab <i className="fas fa-external-link-alt ml-1"></i>
                            </a>
                        )}
                        <div className="text-xs text-gray-400 mt-2 p-2 bg-black/30 rounded-md">
                            <i className="fas fa-info-circle mr-1.5"></i>
                            Use this URL in an N8N 'Webhook' node to send real-time events to this app. Powered by webhook.site for demonstration.
                        </div>
                    </div>
                </div>

                <div className="p-6 border-t border-white/10 flex justify-end gap-3">
                    <button onClick={onClose} className="px-5 py-2.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors font-semibold text-sm">Cancel</button>
                    <button onClick={handleSave} className="px-5 py-2.5 rounded-lg bg-gradient-to-br from-red-600 to-orange-800 hover:from-red-700 font-semibold text-sm">Save Settings</button>
                </div>
            </div>
        </div>
    );
};