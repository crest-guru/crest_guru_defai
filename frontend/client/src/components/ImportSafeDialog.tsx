import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion, AnimatePresence } from "framer-motion";
import { useToast } from "@/hooks/use-toast";

interface ImportSafeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function ImportSafeDialog({ open, onOpenChange }: ImportSafeDialogProps) {
  const [safeAddress, setSafeAddress] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const { toast } = useToast();

  const handleVerifyAndImport = async () => {
    if (!safeAddress) {
      toast({
        title: "Error",
        description: "Please enter a Safe address",
        variant: "destructive",
      });
      return;
    }

    setIsVerifying(true);
    // TODO: Implement actual signature request
    try {
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate verification
      toast({
        title: "Signature Required",
        description: "Please sign the message to import your Safe wallet",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to verify Safe address",
        variant: "destructive",
      });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-gradient-to-b from-background/90 to-background/70 backdrop-blur-lg border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-2xl bg-gradient-to-r from-[#4cc9f0] to-[#7209b7] bg-clip-text text-transparent">
            Import Safe Wallet
          </DialogTitle>
          <DialogDescription>
            Enter your existing Safe address to import
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          <div className="space-y-2">
            <Input
              value={safeAddress}
              onChange={(e) => setSafeAddress(e.target.value)}
              placeholder="Safe Address (0x...)"
              className="bg-background/50 border-primary/20"
            />
          </div>
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
            >
              <Button
                onClick={handleVerifyAndImport}
                disabled={isVerifying}
                className="w-full cosmic-button text-white"
              >
                {isVerifying ? "Verifying..." : "Verify & Import"}
              </Button>
            </motion.div>
          </AnimatePresence>
        </div>
      </DialogContent>
    </Dialog>
  );
}