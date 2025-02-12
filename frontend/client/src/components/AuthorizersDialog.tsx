import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect } from "react";
import { useWeb3 } from "@/context/Web3Context";
import { useAuthorizers } from "@/context/AuthorizersContext";
import { ethers } from "ethers";
import { useToast } from "@/hooks/use-toast";

const RPC_URL = "https://rpc.soniclabs.com";
const CHAIN_ID = 146;

interface AuthorizerInfo {
  address: string;
  name?: string;
}

export default function AuthorizersDialog({ 
  open, 
  onOpenChange 
}: { 
  open: boolean; 
  onOpenChange: (open: boolean) => void;
}) {
  const { authorizers } = useAuthorizers();
  const { account } = useWeb3();
  const { toast } = useToast();
  const [maxAmount, setMaxAmount] = useState("");
  const [authorizersInfo, setAuthorizersInfo] = useState<{
    approve?: AuthorizerInfo;
    silo?: AuthorizerInfo;
  }>({});
  const [isLoading, setIsLoading] = useState(false);

  // ABI для вызова функций
  const authorizerABI = [
    "function _NAME() view returns (string)",
    "function setMaxAmount(uint256) external"
  ];

  useEffect(() => {
    if (open && authorizers.approveAuthorizer && authorizers.siloAuthorizer) {
      fetchAuthorizersNames();
    }
  }, [open, authorizers]);

  const fetchAuthorizersNames = async () => {
    try {
      const provider = new ethers.JsonRpcProvider(RPC_URL);

      const approveContract = new ethers.Contract(
        authorizers.approveAuthorizer!,
        authorizerABI,
        provider
      );
      const siloContract = new ethers.Contract(
        authorizers.siloAuthorizer!,
        authorizerABI,
        provider
      );

      const [approveName, siloName] = await Promise.all([
        approveContract._NAME(),
        siloContract._NAME()
      ]);

      setAuthorizersInfo({
        approve: {
          address: authorizers.approveAuthorizer!,
          name: approveName
        },
        silo: {
          address: authorizers.siloAuthorizer!,
          name: siloName
        }
      });
    } catch (error) {
      console.error("Failed to fetch authorizer names:", error);
      toast({
        title: "Error",
        description: "Failed to fetch authorizer names",
        variant: "destructive",
      });
    }
  };

  const handleSetMaxAmount = async () => {
    if (!account || !maxAmount || !authorizers.siloAuthorizer) return;

    setIsLoading(true);
    try {
      // Проверяем, что есть window.ethereum
      if (!window.ethereum) {
        throw new Error("Please install MetaMask");
      }

      // Переключаемся на нужную сеть
      try {
        await window.ethereum.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: `0x${CHAIN_ID.toString(16)}` }],
        });
      } catch (switchError: any) {
        // Если сеть не добавлена, добавляем её
        if (switchError.code === 4902) {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [{
              chainId: `0x${CHAIN_ID.toString(16)}`,
              chainName: 'Sonic',
              nativeCurrency: {
                name: 'RON',
                symbol: 'RON',
                decimals: 18
              },
              rpcUrls: [RPC_URL],
            }],
          });
        } else {
          throw switchError;
        }
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      
      // Создаем контракт
      const contract = new ethers.Contract(
        authorizers.siloAuthorizer,
        authorizerABI,
        signer
      );

      // Отправляем транзакцию
      toast({
        title: "Sending Transaction",
        description: "Please confirm the transaction in your wallet",
      });

      const tx = await contract.setMaxAmount(ethers.parseEther(maxAmount));
      
      toast({
        title: "Transaction Sent",
        description: "Waiting for confirmation...",
      });

      await tx.wait();

      toast({
        title: "Success",
        description: "Max amount has been set successfully",
      });

      onOpenChange(false); // Закрываем диалог после успешной транзакции
    } catch (error: any) {
      console.error("Failed to set max amount:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to set max amount",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>DeFAI Assistant</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {authorizersInfo.approve && (
            <div className="space-y-2">
              <h4 className="font-medium">Approve Authorizer</h4>
              <p className="text-sm text-muted-foreground break-all">
                {authorizersInfo.approve.address}
              </p>
              {authorizersInfo.approve.name && (
                <p className="text-sm">Name: {authorizersInfo.approve.name}</p>
              )}
            </div>
          )}

          {authorizersInfo.silo && (
            <div className="space-y-2">
              <h4 className="font-medium">Silo Authorizer</h4>
              <p className="text-sm text-muted-foreground break-all">
                {authorizersInfo.silo.address}
              </p>
              {authorizersInfo.silo.name && (
                <p className="text-sm">Name: {authorizersInfo.silo.name}</p>
              )}
              
              <div className="flex gap-2 items-center">
                <Input
                  type="number"
                  placeholder="Max Amount"
                  value={maxAmount}
                  onChange={(e) => setMaxAmount(e.target.value)}
                />
                <Button 
                  onClick={handleSetMaxAmount}
                  disabled={isLoading || !maxAmount || !account}
                >
                  {isLoading ? "Setting..." : "Set Max"}
                </Button>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
} 