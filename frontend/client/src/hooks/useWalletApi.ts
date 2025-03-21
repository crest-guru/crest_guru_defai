import { useToast } from "@/hooks/use-toast";
import { useAuthorizers } from "@/context/AuthorizersContext";
import { ethers } from "ethers";

const RPC_URL = import.meta.env.VITE_RPC_URL;
const API_BASE_URL = import.meta.env.VITE_API_URL;

export const walletEvents = new EventTarget();
export const WALLET_CREATED_EVENT = 'walletCreated';
export const WALLET_INFO_EVENT = 'walletInfo';
export const AI_RESPONSE_EVENT = 'aiResponse';

interface WalletResponse {
  safe_address: string;
  cobo_address: string;
  approve_authorizer_address: string;
  transfer_authorizer_address: string;
}

interface WalletInfo {
  data: {
    agent_address: string;
    agent_key: string;
    cobo_address: string;
    safe_address: string;
  };
  status: string;
}

interface AIRequest {
  user_address: string;
  request: string;
}

export function useWalletApi() {
  const { toast } = useToast();
  const { setAuthorizers } = useAuthorizers();

  const getWalletInfo = async (userAddress: string): Promise<WalletInfo | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/wallet/info?address=${userAddress}`);
      
      if (!response.ok) {
        throw new Error('Failed to get wallet info');
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        walletEvents.dispatchEvent(new CustomEvent(WALLET_INFO_EVENT, { 
          detail: data.data 
        }));
      }

      return data;
    } catch (error) {
      console.error('Failed to get wallet info:', error);
      return null;
    }
  };

  const createWallet = async (userAddress: string): Promise<WalletResponse | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/wallet/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ address: userAddress }),
      });

   
      console.log('Response status:', response.status);
      const responseText = await response.text();
      console.log('Response text:', responseText);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      
      const data = JSON.parse(responseText);
      
      
      setAuthorizers({
        approveAuthorizer: data.approve_authorizer_address,
        siloAuthorizer: data.silo_authorizer_address
      });

      walletEvents.dispatchEvent(new CustomEvent(WALLET_CREATED_EVENT, { 
        detail: data 
      }));

      
      await getWalletInfo(userAddress);

      toast({
        title: "Wallet Created",
        description: `Safe Address: ${data.safe_address.slice(0, 6)}...${data.safe_address.slice(-4)}`,
      });

      return data;
    } catch (error) {
      console.error('Network error:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to create wallet. Please try again.",
        variant: "destructive",
      });
      return null;
    }
  };

  const checkTransactionStatus = async (txHash: string): Promise<"success" | "failed" | null> => {
    try {
      // Check status for 30 seconds
      for (let i = 0; i < 30; i++) {
        const provider = new ethers.JsonRpcProvider(RPC_URL);
        const receipt = await provider.getTransactionReceipt(txHash);

        if (receipt) {
          return receipt.status ? "success" : "failed";
        }

        // Wait 1 second before next check
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      return null;
    } catch (error) {
      console.error('Failed to check transaction status:', error);
      return null;
    }
  };

  const sendAIRequest = async (wallet: string, request: string): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai_request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          request: request,
          wallet: wallet,
        } as AIRequest),
      });

      if (!response.ok) {
        throw new Error('Failed to process AI request');
      }

      const data = await response.json();

      // If we got transaction hash, start RPC checks
      if (data.tx_hash) {
        // Show initial message
        walletEvents.dispatchEvent(new CustomEvent(AI_RESPONSE_EVENT, { 
          detail: {
            status: "pending",
            message: "Transaction sent",
            tx_hash: data.tx_hash
          }
        }));

        // Check actual status via RPC
        const txStatus = await checkTransactionStatus(data.tx_hash);
        
        // Show result only if we got final status
        if (txStatus) {
          walletEvents.dispatchEvent(new CustomEvent(AI_RESPONSE_EVENT, { 
            detail: {
              status: txStatus,
              message: txStatus === "success" ? "Transaction successful" : "Transaction failed (reverted)",
              tx_hash: data.tx_hash,
              finalStatus: true
            }
          }));
        }
      } else {
        // Regular response without transaction
        walletEvents.dispatchEvent(new CustomEvent(AI_RESPONSE_EVENT, { 
          detail: data
        }));
      }

      return data;
    } catch (error) {
      console.error('AI request error:', error);
      walletEvents.dispatchEvent(new CustomEvent('system', { 
        detail: 'Failed to process AI request. Please try again.' 
      }));
      return null;
    }
  };

  return { createWallet, getWalletInfo, sendAIRequest };
} 