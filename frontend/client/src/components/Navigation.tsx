import { Link } from "wouter";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useDialog } from "@/context/DialogContext";
import { useWeb3 } from "@/context/Web3Context";

export default function Navigation() {
  const { setDialogOpen } = useDialog();
  const { connectWallet, disconnectWallet, isConnecting, isConnected, account } = useWeb3();

  const handleConnect = async () => {
    if (isConnected) {
      await disconnectWallet();
      return;
    }

    const success = await connectWallet();
    if (success) {
      setTimeout(() => setDialogOpen(true), 500);
    }
  };

  // Function to abbreviate the wallet address
  const abbreviateAddress = (address: string) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <motion.nav 
      className="fixed w-full z-50 backdrop-blur-md bg-background/50 border-b border-border"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/">
          <span className="text-lg font-medium bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent cursor-pointer">
            Crest Guru
          </span>
        </Link>

        <div className="flex gap-6 items-center">
          <Button 
            variant="ghost"
            size="sm"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            onClick={() => {
              document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            Features
          </Button>
          <Button 
            size="sm"
            className="bg-primary hover:opacity-90 transition-opacity"
            onClick={handleConnect}
            disabled={isConnecting}
          >
            {isConnecting 
              ? "Connecting..." 
              : isConnected 
                ? abbreviateAddress(account)
                : "Connect Wallet"
            }
          </Button>
        </div>
      </div>
    </motion.nav>
  );
}