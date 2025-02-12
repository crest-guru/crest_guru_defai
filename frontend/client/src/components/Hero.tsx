import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useDialog } from "@/context/DialogContext";
import { useWeb3 } from "@/context/Web3Context";

export default function Hero() {
  const { setDialogOpen } = useDialog();
  const { connectWallet, isConnecting, isConnected } = useWeb3();

  const handleConnect = async () => {
    if (isConnected) {
      setDialogOpen(true);
      return;
    }

    await connectWallet();
  };

  return (
    <div className="min-h-[60vh] relative flex items-center justify-center">
      <div className="container mx-auto px-4 relative z-10 text-center">
        <motion.div 
          className="max-w-xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <motion.h1 
            className="text-4xl md:text-5xl font-medium mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <span className="bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent">
              Secure your assets
            </span>
          </motion.h1>

          <motion.p 
            className="text-base text-muted-foreground mb-6 max-w-md mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            Protect your digital assets with enterprise-grade security
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <Button 
              size="lg" 
              className="min-w-[200px] bg-primary hover:opacity-90 transition-opacity"
              onClick={handleConnect}
              disabled={isConnecting}
            >
              {isConnecting ? "Connecting..." : isConnected ? "Open Assistant" : "Your personal DeFAI Assistant"}
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}