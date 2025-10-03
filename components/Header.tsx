import React from 'react';
import { ConnectionStatus, LLMProvider } from '../types';

interface StatusIndicatorProps {
    name: string;
    status?: ConnectionStatus;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ name, status = 'connected' }) => (
    <div className="flex items-center gap-2.5 text-sm">
        <div className={`w-3.5 h-3.5 rounded-full ${status === 'connected' ? 'bg-emerald-500 shadow-[0_0_14px_#10b981]' : 'bg-red-500'}`}></div>
        <span>{name}</span>
    </div>
);

interface HeaderProps {
    llmStatus: ConnectionStatus;
    n8nStatus: ConnectionStatus;
    liquidAudioStatus: ConnectionStatus;
    webhookStatus: ConnectionStatus;
    provider: LLMProvider;
    onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({ llmStatus, n8nStatus, liquidAudioStatus, webhookStatus, provider, onOpenSettings }) => {
    return (
        <header className="border-b border-white/10 bg-black/40 backdrop-blur-lg p-5 mb-7 rounded-2xl flex justify-between items-center">
            <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-red-600 to-orange-900 rounded-xl flex items-center justify-center text-3xl">
                    <i className="fas fa-project-diagram"></i>
                </div>
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 via-amber-400 to-sky-400 text-transparent bg-clip-text">Liquid Audio Agent</h1>
                    <p className="text-sm opacity-80 text-red-300">LangGraph Stateful Workflows + N8N + LM Studio</p>
                </div>
            </div>
            <div className="flex items-center gap-4">
                <div className="hidden md:flex items-center gap-5">
                    <StatusIndicator name="LLM Provider" status={llmStatus} />
                    <StatusIndicator name="Liquid Audio" status={liquidAudioStatus} />
                    <StatusIndicator name="N8N" status={n8nStatus} />
                    <StatusIndicator name="N8N Webhook" status={webhookStatus} />
                    <StatusIndicator name="LangGraph" />
                </div>
                 <button 
                    onClick={onOpenSettings} 
                    className="w-11 h-11 rounded-lg bg-white/10 hover:bg-white/20 transition-colors flex items-center justify-center text-lg"
                    aria-label="Open settings"
                >
                    <i className="fas fa-cog"></i>
                </button>
            </div>
        </header>
    );
};
