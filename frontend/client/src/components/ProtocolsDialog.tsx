import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface ProtocolsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function ProtocolsDialog({ open, onOpenChange }: ProtocolsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-gradient-to-b from-background/90 to-background/70 backdrop-blur-lg border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-2xl bg-gradient-to-r from-[#4cc9f0] to-[#7209b7] bg-clip-text text-transparent">
            List of Protocols
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-2 pt-4">
          <ul className="space-y-2 text-foreground/80">
            <li className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-primary rounded-full"></span>
              <span>Aave V3 Protocol</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-primary rounded-full"></span>
              <span>Uniswap V3</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-primary rounded-full"></span>
              <span>Compound Finance</span>
            </li>
          </ul>
        </div>
      </DialogContent>
    </Dialog>
  );
}
