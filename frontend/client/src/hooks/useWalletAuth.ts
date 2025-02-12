import { ethers } from 'ethers';
import { useState } from 'react';

const SIGNATURE_MESSAGE = "Welcome to our app! Please sign this message to verify your wallet ownership.";

export function useWalletAuth() {
  const [isVerified, setIsVerified] = useState(false);
  
  const verifyWallet = async (provider: any): Promise<string> => {
    try {
      const signer = provider.getSigner();
      const address = await signer.getAddress();
      
      const signature = await signer.signMessage(SIGNATURE_MESSAGE);
      
      const recoveredAddress = ethers.verifyMessage(SIGNATURE_MESSAGE, signature);
      
      if (recoveredAddress.toLowerCase() === address.toLowerCase()) {
        setIsVerified(true);
        return address;
      } else {
        throw new Error('Signature verification failed');
      }
      
    } catch (error) {
      setIsVerified(false);
      throw error;
    }
  };

  return {
    isVerified,
    verifyWallet
  };
} 