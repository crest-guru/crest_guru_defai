import { useState } from 'react';
import { ethers } from 'ethers';
import { useWalletAuth } from './useWalletAuth';

export function useWallet() {
  const [address, setAddress] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { verifyWallet, isVerified } = useWalletAuth();

  const connectWallet = async () => {
    try {
      if (!window.ethereum) {
        throw new Error('Please install MetaMask');
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      
      const verifiedAddress = await verifyWallet(provider);
      
      setAddress(verifiedAddress);
      setIsConnected(true);
      
      return verifiedAddress;
      
    } catch (error: any) {
      console.error('Failed to connect wallet:', error);
      throw error;
    }
  };

  const disconnectWallet = () => {
    setAddress(null);
    setIsConnected(false);
  };

  return {
    address,
    isConnected,
    isVerified,
    connectWallet,
    disconnectWallet
  };
} 