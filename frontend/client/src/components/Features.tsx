import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Wallet } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import ImportSafeDialog from "./ImportSafeDialog";
import CreateSafeDialog from "./CreateSafeDialog";
import { Terminal } from "@/components/ui/terminal";
import { useWeb3 } from "@/context/Web3Context";
import { useWalletApi } from "@/hooks/useWalletApi";
import { useAuthorizers } from "@/context/AuthorizersContext";
import AuthorizersDialog from "./AuthorizersDialog";

export default function Features() {
  const [importSafeDialogOpen, setImportSafeDialogOpen] = useState(false);
  const [createSafeDialogOpen, setCreateSafeDialogOpen] = useState(false);
  const { account } = useWeb3();
  const { getWalletInfo } = useWalletApi();
  const [authorizersDialogOpen, setAuthorizersDialogOpen] = useState(false);
  const { authorizers } = useAuthorizers();

  const handleGoToSafe = async () => {
    if (!account) return;
    
    const walletInfo = await getWalletInfo(account);
    if (walletInfo?.status === 'success' && walletInfo.data.safe_address) {
      const safeUrl = `https://app.safe.global/settings/setup?safe=sonic:${walletInfo.data.safe_address}`;
      window.open(safeUrl, '_blank');
    }
  };

  return (
    <section id="features" className="py-6">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
          >
            <Card className="border-border bg-background/50 backdrop-blur-sm">
              <div className="p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Wallet className="h-5 w-5 text-primary" />
                  <h3 className="font-medium">Secure Wallet</h3>
                </div>

                <div className="flex gap-2 mb-4">
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="text-sm bg-background/50 hover:bg-primary/5"
                    onClick={() => setImportSafeDialogOpen(true)}
                  >
                    Import Safe (TBD)
                  </Button>
                  <Button 
                    variant="outline"
                    size="sm"
                    className="text-sm bg-background/50 hover:bg-primary/5"
                    onClick={() => setCreateSafeDialogOpen(true)}
                  >
                    Create Agent Wallet
                  </Button>
                  <Button 
                    variant="outline"
                    size="sm"
                    className="text-sm bg-background/50 hover:bg-primary/5"
                    onClick={handleGoToSafe}
                    disabled={!account}
                  >
                    Go To Safe
                  </Button>
                  <Button 
                    variant="outline"
                    size="sm"
                    className="text-sm bg-background/50 hover:bg-primary/5"
                    onClick={() => setAuthorizersDialogOpen(true)}
                    disabled={!account || !authorizers.approveAuthorizer}
                  >
                    DeFAI Assistant
                  </Button>
                </div>

                <Terminal />
              </div>
            </Card>
          </motion.div>
        </div>
      </div>

      <ImportSafeDialog
        open={importSafeDialogOpen}
        onOpenChange={setImportSafeDialogOpen}
      />
      <CreateSafeDialog
        open={createSafeDialogOpen}
        onOpenChange={setCreateSafeDialogOpen}
      />
      <AuthorizersDialog
        open={authorizersDialogOpen}
        onOpenChange={setAuthorizersDialogOpen}
      />
    </section>
  );
}