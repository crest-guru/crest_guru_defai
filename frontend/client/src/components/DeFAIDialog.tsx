import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { motion } from "framer-motion";
import { useWeb3 } from "@/context/Web3Context";

interface DeFAIDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function DeFAIDialog({ open, onOpenChange }: DeFAIDialogProps) {
  const { isConnected } = useWeb3();
  const [message, setMessage] = useState("");

  if (!isConnected) {
    return null;
  }

  const handleSubmit = () => {
    // TODO: Implement message sending functionality
    console.log("Message to DeFAI:", message);
    setMessage("");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-gradient-to-b from-background/90 to-background/70 backdrop-blur-lg border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-2xl bg-gradient-to-r from-[#4cc9f0] to-[#7209b7] bg-clip-text text-transparent">
            DeFAI Assistant
          </DialogTitle>
          <DialogDescription className="text-foreground/80">
            Write a message to your personal DeFAI assistant
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="How can I help you today?"
            className="min-h-[120px] bg-background/50 border-primary/20"
          />
          <Button
            onClick={handleSubmit}
            className="w-full bg-[#4cc9f0] hover:bg-[#7209b7] text-[#0d1b2a] hover:text-white transition-all duration-300"
          >
            Send Message
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
