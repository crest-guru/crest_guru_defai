import { useState, useEffect } from 'react';
import { ScrollArea } from './scroll-area';
import { useWeb3 } from '@/context/Web3Context';
import { walletEvents, WALLET_CREATED_EVENT, WALLET_INFO_EVENT, AI_RESPONSE_EVENT, useWalletApi } from '@/hooks/useWalletApi';

interface Message {
  type: 'system' | 'user' | 'assistant' | 'response';
  content: string | object;
  timestamp: Date;
}

export function Terminal() {
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'system',
      content: 'DeFAI Terminal v1.0.0 initialized. Waiting for wallet connection...',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const { account } = useWeb3();
  const { sendAIRequest } = useWalletApi();

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message]);
  };

  const formatResponse = (obj: any): string => {
    return Object.entries(obj)
      .map(([key, value]) => `${key}: "${value}"`)
      .join('\n');
  };

  const handleWalletCreated = (event: CustomEvent) => {
    addMessage({
      type: 'system',
      content: 'Wallet creation successful. Details:',
      timestamp: new Date()
    });
    
    addMessage({
      type: 'response',
      content: event.detail,
      timestamp: new Date()
    });

    addMessage({
      type: 'system',
      content: `Please fund your safe_address (this is your main storage) and agent_address for gas, as this wallet will be used for on-chain operations.`,
      timestamp: new Date()
    });
  };

  const handleWalletInfo = (event: CustomEvent) => {
    addMessage({
      type: 'system',
      content: 'Wallet information retrieved:',
      timestamp: new Date()
    });
    
    addMessage({
      type: 'response',
      content: event.detail,
      timestamp: new Date()
    });
  };

  const handleSystemMessage = (event: CustomEvent) => {
    addMessage({
      type: 'system',
      content: event.detail,
      timestamp: new Date()
    });
  };

  const handleAIResponse = (event: CustomEvent) => {
    const response = event.detail;

    // Если есть tx_hash, форматируем сообщение специальным образом
    if (response.tx_hash) {
      // Для начального сообщения о транзакции
      if (response.status === "pending" && !response.finalStatus) {
        addMessage({
          type: 'system',
          content: response.message,
          timestamp: new Date()
        });

        addMessage({
          type: 'response',
          content: `Transaction Hash: ${response.tx_hash}`,
          timestamp: new Date()
        });
      }
      // Для финального статуса
      else if (response.finalStatus) {
        addMessage({
          type: 'system',
          content: response.message,
          timestamp: new Date()
        });
      }
    } else {
      // Обычный ответ без транзакции
      addMessage({
        type: 'response',
        content: response,
        timestamp: new Date()
      });
    }
  };

  useEffect(() => {
    walletEvents.addEventListener(WALLET_CREATED_EVENT, handleWalletCreated as EventListener);
    walletEvents.addEventListener(WALLET_INFO_EVENT, handleWalletInfo as EventListener);
    walletEvents.addEventListener('system', handleSystemMessage as EventListener);
    walletEvents.addEventListener(AI_RESPONSE_EVENT, handleAIResponse as EventListener);

    return () => {
      walletEvents.removeEventListener(WALLET_CREATED_EVENT, handleWalletCreated as EventListener);
      walletEvents.removeEventListener(WALLET_INFO_EVENT, handleWalletInfo as EventListener);
      walletEvents.removeEventListener('system', handleSystemMessage as EventListener);
      walletEvents.removeEventListener(AI_RESPONSE_EVENT, handleAIResponse as EventListener);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !account) return;

    const userMessage: Message = {
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    addMessage(userMessage);
    
    await sendAIRequest(account, input);
    
    setInput('');
  };

  return (
    <div className="bg-[#1E1E1E] rounded-lg p-4 font-mono text-sm">
      <ScrollArea className="h-[400px] mb-4">
        <div className="space-y-2">
          {messages.map((msg, i) => (
            <div 
              key={i} 
              className={`
                ${msg.type === 'system' ? 'text-yellow-500' : ''}
                ${msg.type === 'user' ? 'text-green-500' : ''}
                ${msg.type === 'assistant' ? 'text-blue-500' : ''}
                ${msg.type === 'response' ? 'text-cyan-500' : ''}
              `}
            >
              <span className="opacity-70">
                [{msg.timestamp.toLocaleTimeString()}]
              </span>{' '}
              {typeof msg.content === 'string' ? (
                msg.content
              ) : (
                <pre className="mt-1 ml-4 whitespace-pre">
                  {formatResponse(msg.content)}
                </pre>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 bg-[#2D2D2D] border border-gray-700 rounded px-2 py-1 text-white focus:outline-none focus:border-primary"
          placeholder={account ? "Type your request..." : "Please connect wallet first..."}
          disabled={!account}
        />
        <button
          type="submit"
          className="px-3 py-1 bg-primary/10 text-primary rounded hover:bg-primary/20 disabled:opacity-50"
          disabled={!account}
        >
          Send
        </button>
      </form>
    </div>
  );
} 