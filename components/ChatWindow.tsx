import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types';

interface ChatWindowProps {
    messages: Message[];
    selectedModelName: string;
    isProcessing: boolean;
    isListening: boolean;
    setIsListening: React.Dispatch<React.SetStateAction<boolean>>;
    onSendMessage: (content: string) => void;
}

const TypingIndicator: React.FC = () => (
    <div className="flex items-start gap-4.5 self-start max-w-[90%]">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-red-600 to-orange-900 flex items-center justify-center flex-shrink-0 text-2xl">
            <i className="fas fa-robot"></i>
        </div>
        <div className="px-5 py-4 bg-white/10 border border-white/15 rounded-2xl rounded-bl-lg flex gap-2.5">
            <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce"></div>
            <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:0.2s]"></div>
            <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:0.4s]"></div>
        </div>
    </div>
);

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
    const isAssistant = message.role === 'assistant';
    return (
        <div className={`flex items-start gap-5 max-w-[90%] ${isAssistant ? 'self-start' : 'self-end flex-row-reverse'}`}>
            <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 text-2xl ${isAssistant ? 'bg-gradient-to-br from-red-600 to-orange-900' : 'bg-gradient-to-br from-cyan-500 to-blue-500'}`}>
                <i className={`fas ${isAssistant ? 'fa-robot' : 'fa-user'}`}></i>
            </div>
            <div>
                <div className={`px-5 py-4 rounded-2xl text-base leading-relaxed ${isAssistant ? 'bg-white/10 border border-white/15 rounded-bl-lg' : 'bg-gradient-to-br from-cyan-500 to-blue-500 text-white rounded-br-lg'}`} dangerouslySetInnerHTML={{ __html: message.content }}>
                </div>
                {message.tools && (
                    <div className="flex gap-2.5 mt-3 flex-wrap">
                        {message.tools.map(tool => (
                            <span key={tool} className="bg-indigo-500/20 text-indigo-300 px-3 py-1.5 rounded-full text-xs border border-indigo-500/30 font-medium">{tool}</span>
                        ))}
                    </div>
                )}
                {message.langGraphSteps && (
                     <div className="flex gap-2 mt-2.5 flex-wrap">
                        {message.langGraphSteps.map(step => (
                            <span key={step.name} className="bg-purple-500/20 text-purple-300 px-2.5 py-1 rounded-full text-[11px] border border-purple-500/30">
                                <i className="fas fa-check-circle mr-1.5 opacity-80"></i>{step.name}
                            </span>
                        ))}
                    </div>
                )}
                <div className={`text-xs opacity-70 mt-2.5 ${isAssistant ? 'text-left' : 'text-right'}`}>{message.time}</div>
            </div>
        </div>
    );
};

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, selectedModelName, isProcessing, isListening, setIsListening, onSendMessage }) => {
    const [inputValue, setInputValue] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages, isProcessing]);
    
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            const scrollHeight = textareaRef.current.scrollHeight;
            textareaRef.current.style.height = `${Math.min(scrollHeight, 150)}px`;
        }
    }, [inputValue]);

    const handleSend = () => {
        onSendMessage(inputValue);
        setInputValue('');
    };

    const handleMicClick = () => {
        setIsListening(prev => !prev);
        if(!isListening) {
             setTimeout(() => {
                const voiceInputs = [
                    "Execute a full LangGraph workflow with Liquid Audio processing and Memento memory integration",
                    "Process this through the stateful agent pipeline using all integrated systems",
                    "Run the complete 7-step LangGraph workflow with LM Studio model selection",
                ];
                setInputValue(voiceInputs[Math.floor(Math.random() * voiceInputs.length)]);
                setIsListening(false);
            }, 3000);
        }
    };
    
    return (
        <div className="bg-black/50 backdrop-blur-lg border border-white/10 rounded-2xl flex flex-col h-[75vh] lg:h-auto">
            <div className="p-5 border-b border-white/10 flex justify-between items-center">
                <div className="flex items-center gap-4 font-semibold flex-wrap">
                    <i className="fas fa-robot"></i>
                    <span>Stateful Agent</span>
                    <div className="bg-red-600/20 px-4 py-1.5 rounded-full text-sm text-red-300 border border-red-600/30 truncate max-w-xs">{selectedModelName}</div>
                    <div className="bg-blue-500/20 px-4 py-1.5 rounded-full text-sm text-blue-300 border border-blue-500/30">Active Agent</div>
                    <div className="bg-purple-500/20 px-4 py-1.5 rounded-full text-sm text-purple-300 border border-purple-500/30">LangGraph Active</div>
                </div>
            </div>
            <div className="flex-1 p-5 overflow-y-auto flex flex-col gap-5">
                {messages.map((msg, index) => (
                    <MessageBubble key={index} message={msg} />
                ))}
                {isProcessing && <TypingIndicator />}
                <div ref={messagesEndRef} />
            </div>
            <div className="p-5 border-t border-white/10">
                <div className="flex gap-5 items-end">
                    <button onClick={handleMicClick} className={`mic-btn flex-shrink-0 w-16 h-16 rounded-full text-2xl text-white transition-all duration-200 flex items-center justify-center shadow-lg ${isListening ? 'listening bg-gradient-to-br from-red-500 to-orange-500 shadow-red-500/40' : 'bg-gradient-to-br from-red-600 to-orange-900 shadow-red-600/40'}`}>
                        <i className={`fas ${isListening ? 'fa-microphone-slash' : 'fa-microphone'}`}></i>
                    </button>
                    <div className="relative flex-1">
                        <textarea
                            ref={textareaRef}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                            placeholder="Speak or type... LangGraph will manage the stateful workflow..."
                            className="w-full min-h-[64px] max-h-[150px] p-4 pr-16 rounded-3xl border border-white/20 bg-white/10 text-white placeholder-white/50 focus:border-red-600 focus:bg-white/15 outline-none resize-none"
                            rows={1}
                            disabled={isProcessing}
                        />
                        <button onClick={handleSend} className="absolute right-4 bottom-4 w-11 h-11 rounded-full bg-gradient-to-br from-red-600 to-orange-900 text-white flex items-center justify-center" disabled={isProcessing || !inputValue.trim()}>
                            <i className="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
                 {isListening && (
                    <div className="text-center text-red-500 text-base mt-3.5 font-semibold animate-pulse">
                        <i className="fas fa-wave-square"></i> Listening with Liquid Audio & LangGraph State...
                    </div>
                )}
            </div>
        </div>
    );
};
