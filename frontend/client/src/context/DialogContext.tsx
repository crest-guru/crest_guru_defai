import { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { useWeb3 } from "./Web3Context";

interface DialogContextType {
  isDialogOpen: boolean;
  setDialogOpen: (open: boolean) => void;
}

const DialogContext = createContext<DialogContextType | undefined>(undefined);

export function DialogProvider({ children }: { children: ReactNode }) {
  const [isDialogOpen, setDialogOpen] = useState(false);
  const { isConnected } = useWeb3();

  useEffect(() => {
    if (!isConnected) {
      setDialogOpen(false);
    }
  }, [isConnected]);

  return (
    <DialogContext.Provider value={{ isDialogOpen, setDialogOpen }}>
      {children}
    </DialogContext.Provider>
  );
}

export function useDialog() {
  const context = useContext(DialogContext);
  if (context === undefined) {
    throw new Error("useDialog must be used within a DialogProvider");
  }
  return context;
}
