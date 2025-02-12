import { useWallet } from '../hooks/useWallet';
import { toast } from 'react-hot-toast';

export function WalletConnect() {
  const { connectWallet, disconnectWallet, isConnected, address } = useWallet();

  const handleConnect = async () => {
    try {
      await connectWallet();
      toast.success('Wallet connected and verified!');
    } catch (error: any) {
      if (error.message.includes('Please install MetaMask')) {
        toast.error('Please install MetaMask');
      } else if (error.message.includes('verification failed')) {
        toast.error('Failed to verify wallet ownership');
      } else {
        toast.error('Failed to connect wallet');
      }
    }
  };

  return (
    <div>
      {!isConnected ? (
        <button 
          onClick={handleConnect}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Connect Wallet
        </button>
      ) : (
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {address?.slice(0, 6)}...{address?.slice(-4)}
          </span>
          <button 
            onClick={disconnectWallet}
            className="px-4 py-2 bg-red-500 text-white rounded"
          >
            Disconnect
          </button>
        </div>
      )}
    </div>
  );
} 