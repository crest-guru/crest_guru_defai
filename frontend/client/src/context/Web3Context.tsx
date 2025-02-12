import { createContext, useContext, useState, ReactNode } from "react";
import { useToast } from "@/hooks/use-toast";
import { ethers } from "ethers";

interface Web3ContextType {
  isConnecting: boolean;
  isConnected: boolean;
  connectWallet: () => Promise<boolean>;
  disconnectWallet: () => Promise<void>;
  account: string | null;
}

const SIGNATURE_MESSAGE = "Welcome to our app! Please sign this message to verify your wallet ownership.";

const Web3Context = createContext<Web3ContextType | undefined>(undefined);

export function Web3Provider({ children }: { children: ReactNode }) {
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState<string | null>(null);
  const { toast } = useToast();

  const connectWallet = async (): Promise<boolean> => {
    setIsConnecting(true);

    try {
      if (!window.ethereum) {
        throw new Error("Please install MetaMask");
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const address = await signer.getAddress();
      
      const signature = await signer.signMessage(SIGNATURE_MESSAGE);
      
      const recoveredAddress = ethers.verifyMessage(SIGNATURE_MESSAGE, signature);
      
      if (recoveredAddress.toLowerCase() !== address.toLowerCase()) {
        throw new Error("Signature verification failed");
      }

      setAccount(address);
      setIsConnected(true);

      toast({
        title: "Wallet Connected",
        description: `Connected to ${address.slice(0, 6)}...${address.slice(-4)}`,
      });

      return true;
    } catch (error: any) {
      let errorMessage = "Could not connect to wallet. Please try again.";
      
      if (error.message.includes("Please install MetaMask")) {
        errorMessage = "Please install MetaMask";
      } else if (error.message.includes("verification failed")) {
        errorMessage = "Failed to verify wallet ownership";
      }

      toast({
        title: "Connection Failed",
        description: errorMessage,
        variant: "destructive",
      });
      return false;
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectWallet = async (): Promise<void> => {
    try {
      setAccount(null);
      setIsConnected(false);
      toast({
        title: "Wallet Disconnected",
        description: "Your wallet has been disconnected.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to disconnect wallet. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Web3Context.Provider value={{ 
      isConnecting, 
      isConnected, 
      connectWallet, 
      disconnectWallet, 
      account 
    }}>
      {children}
    </Web3Context.Provider>
  );
}

export function useWeb3() {
  const context = useContext(Web3Context);
  if (context === undefined) {
    throw new Error("useWeb3 must be used within a Web3Provider");
  }
  return context;
}