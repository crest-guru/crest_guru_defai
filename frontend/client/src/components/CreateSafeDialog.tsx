import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useWeb3 } from "@/context/Web3Context";
import { useWalletApi } from "@/hooks/useWalletApi";
import { useState } from "react";
import { Button } from "./ui/button";

interface CreateSafeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function CreateSafeDialog({ open, onOpenChange }: CreateSafeDialogProps) {
  const { account } = useWeb3();
  const { createWallet, getWalletInfo } = useWalletApi();
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = async () => {
    if (!account) return;
    
    setIsCreating(true);
    try {
      const existingWallet = await getWalletInfo(account);
      if (existingWallet) {
        onOpenChange(false);
        return;
      }

      const wallet = await createWallet(account);
      if (wallet) {
        onOpenChange(false);
      }
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create Agent Wallet</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <p className="text-sm text-muted-foreground">
          Generate a new Safe wallet and assign it an operator address using default limits.
          </p>
          <Button 
            onClick={handleCreate} 
            className="w-full"
            disabled={isCreating || !account}
          >
            {isCreating ? "Creating..." : "Create Wallet"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}