import React, { useState } from 'react';
import { Model, MemoryItem, AgentSettings, LangGraphStep, ConnectionStatus, LLMProvider } from '../types';

interface SidebarProps {
    models: Model[];
    selectedModelId: string;
    onSelectModel: (modelId: string) => void;
    memoryItems: MemoryItem[];
    agentSettings: AgentSettings;
    setAgentSettings: React.Dispatch<React.SetStateAction<AgentSettings>>;
    workflowSteps: LangGraphStep[];
    onClearChat: () => void;
    onOpenSettings: () => void;
    llmStatus: ConnectionStatus;
    provider: LLMProvider;
    onRefreshModels: () => Promise<void>;
}

const SidebarCard: React.FC<{ title: string; icon: string; badgeText?: string; badgeColor?: string; children: React.ReactNode; disabled?: boolean }> = ({ title, icon, badgeText, badgeColor, children, disabled = false }) => (
    <div className={`bg-black/50 backdrop-blur-lg border border-white/10 rounded-2xl p-6 ${disabled ? 'opacity-50 pointer-events-none' : ''}`}>
        <h3 className="text-xl font-semibold mb-5 flex items-center gap-3 text-red-200">
            <i className={`fas ${icon}`}></i>
            <span>{title}</span>
            {badgeText && <span className={`text-xs px-2 py-0.5 rounded-full ${badgeColor}`}>{badgeText}</span>}
        </h3>
        {children}
    </div>
);

const ToggleSwitch: React.FC<{ checked: boolean; onChange: (checked: boolean) => void }> = ({ checked, onChange }) => (
    <label className="relative inline-block w-14 h-7">
        <input type="checkbox" className="opacity-0 w-0 h-0" checked={checked} onChange={(e) => onChange(e.target.checked)} />
        <span className={`absolute cursor-pointer top-0 left-0 right-0 bottom-0 rounded-full transition-colors duration-300 ${checked ? 'bg-amber-500' : 'bg-gray-600'}`}></span>
        <span className={`absolute content-[''] h-5 w-5 left-1 bottom-1 bg-white rounded-full transition-transform duration-300 ${checked ? 'translate-x-7' : ''}`}></span>
    </label>
);

const LangGraphWorkflowCard: React.FC<{steps: LangGraphStep[]}> = ({ steps }) => (
    <SidebarCard title="LangGraph Workflow" icon="fa-project-diagram" badgeText="LangGraph" badgeColor="bg-purple-500/20 text-purple-300">
        <div className="flex flex-col gap-3">
            {steps.map((step, index) => (
                <div key={index} className={`p-3 rounded-lg flex items-center gap-3 transition-all duration-300 ${step.active ? 'bg-purple-500/20 border-purple-500/40' : 'bg-white/5 border-transparent'} border`}>
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 ${step.active ? 'bg-purple-500 text-white' : 'bg-gray-600 text-gray-300'}`}>
                        {index + 1}
                    </div>
                    <div className={`text-sm ${step.active ? 'text-purple-200' : 'text-gray-400'}`}>{step.name}</div>
                </div>
            ))}
        </div>
    </SidebarCard>
);


export const Sidebar: React.FC<SidebarProps> = ({ models, selectedModelId, onSelectModel, agentSettings, setAgentSettings, workflowSteps, onClearChat, onOpenSettings, llmStatus, provider, onRefreshModels }) => {
    const [isRefreshing, setIsRefreshing] = useState(false);
    const isLmStudioDisabled = provider !== 'lmstudio' || llmStatus === 'disconnected';

    const handleRefresh = async () => {
        setIsRefreshing(true);
        await onRefreshModels();
        setIsRefreshing(false);
    };
    
    const handleSettingChange = <K extends keyof AgentSettings>(key: K, value: AgentSettings[K]) => {
        setAgentSettings(prev => ({ ...prev, [key]: value }));
    };

    return (
        <aside className="flex flex-col gap-6">
            <SidebarCard 
                title="LM Studio Models" 
                icon="fa-brain" 
                badgeText="LangChain" 
                badgeColor="bg-amber-500/20 text-amber-300"
                disabled={isLmStudioDisabled}
            >
                {isLmStudioDisabled ? (
                     <div className="text-center p-4 rounded-lg bg-yellow-500/10 text-yellow-300 border border-yellow-500/20">
                        Connect to LM Studio in settings to enable model selection.
                    </div>
                ) : (
                    <>
                        <div className="flex flex-col gap-3.5 mb-4">
                            {models.map(model => (
                                <div key={model.id} onClick={() => onSelectModel(model.id)} className={`p-3.5 rounded-xl border cursor-pointer transition-all duration-200 flex justify-between items-center ${selectedModelId === model.id ? 'bg-red-600/20 border-red-600' : 'bg-white/5 border-white/15 hover:bg-white/10'}`}>
                                    <div>
                                        <div className="font-medium text-red-200 text-sm">{model.name}</div>
                                        <div className="text-xs opacity-70 text-red-300">{model.params} parameters • {model.description}</div>
                                    </div>
                                    {selectedModelId === model.id && <i className="fas fa-check-circle text-emerald-400"></i>}
                                </div>
                            ))}
                        </div>
                        <button onClick={handleRefresh} disabled={isRefreshing} className="w-full p-3 rounded-lg border border-white/20 bg-white/10 hover:bg-white/20 transition-colors text-sm flex items-center justify-center gap-2">
                            {isRefreshing ? <><div className="w-5 h-5 border-2 border-white/30 border-t-red-500 rounded-full animate-spin"></div><span>Scanning...</span></> : <><i className="fas fa-sync-alt"></i><span>Refresh LM Studio Models</span></>}
                        </button>
                    </>
                )}
            </SidebarCard>

            <LangGraphWorkflowCard steps={workflowSteps} />

            <SidebarCard title="Agent Configuration" icon="fa-cogs" badgeText="LangChain" badgeColor="bg-amber-500/20 text-amber-300">
                 <div className="flex flex-col gap-2">
                    <div className="flex justify-between items-center p-2">
                        <div className="flex items-center gap-3 text-sm"><i className="fas fa-wave-square text-amber-400 w-5 text-center"></i><span>Liquid Audio</span></div>
                        <ToggleSwitch checked={agentSettings.liquidAudio} onChange={(c) => handleSettingChange('liquidAudio', c)} />
                    </div>
                    <div className="flex justify-between items-center p-2">
                        <div className="flex items-center gap-3 text-sm"><i className="fas fa-memory text-amber-400 w-5 text-center"></i><span>Memento Memory</span></div>
                        <ToggleSwitch checked={agentSettings.mementoMemory} onChange={(c) => handleSettingChange('mementoMemory', c)} />
                    </div>
                     <div className="flex justify-between items-center p-2">
                        <div className="flex items-center gap-3 text-sm"><i className="fas fa-project-diagram text-amber-400 w-5 text-center"></i><span>LangGraph Stateful</span></div>
                        <ToggleSwitch checked={agentSettings.langGraph} onChange={(c) => handleSettingChange('langGraph', c)} />
                    </div>
                    <div className="flex justify-between items-center p-2">
                        <div className="flex items-center gap-3 text-sm"><i className="fas fa-robot text-amber-400 w-5 text-center"></i><span>N8N Tool Calling</span></div>
                        <ToggleSwitch checked={agentSettings.n8nToolCalling} onChange={(c) => handleSettingChange('n8nToolCalling', c)} />
                    </div>
                    <div className="flex justify-between items-center p-2">
                        <div className="flex items-center gap-3 text-sm"><i className="fas fa-brain text-amber-400 w-5 text-center"></i><span>Auto Model Selection</span></div>
                        <ToggleSwitch checked={agentSettings.autoModelSelection} onChange={(c) => handleSettingChange('autoModelSelection', c)} />
                    </div>
                    <div className="flex justify-between items-center p-2">
                        <div className="flex items-center gap-3 text-sm"><i className="fas fa-route text-amber-400 w-5 text-center"></i><span>Reasoning Steps</span></div>
                        <ToggleSwitch checked={agentSettings.reasoningSteps} onChange={(c) => handleSettingChange('reasoningSteps', c)} />
                    </div>
                </div>
            </SidebarCard>

            <SidebarCard title="Quick Actions" icon="fa-bolt">
                <div className="grid grid-cols-2 gap-3.5">
                    <button onClick={onClearChat} className="p-4 rounded-xl bg-white/10 hover:bg-white/20 transition-colors font-medium text-sm">Clear Chat</button>
                    <button onClick={onOpenSettings} className="p-4 rounded-xl bg-white/10 hover:bg-white/20 transition-colors font-medium text-sm">Agent Settings</button>
                    <button className="p-4 rounded-xl bg-gradient-to-br from-red-600 to-orange-900 hover:from-red-700 hover:to-orange-800 transition-all font-medium text-sm col-span-2">New Session</button>
                </div>
            </SidebarCard>
        </aside>
    );
};