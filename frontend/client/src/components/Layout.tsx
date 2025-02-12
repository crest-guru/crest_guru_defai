import Features from "@/components/Features";
import { Button } from "@/components/ui/button";
import { useWeb3 } from "@/context/Web3Context";
import { Wallet } from "lucide-react";

export default function Layout() {
  const { account, isConnected, connectWallet, disconnectWallet } = useWeb3();

  return (
    <div className="min-h-screen bg-gradient-to-b from-background/60 to-background">
      <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 max-w-screen-2xl items-center">
          <div className="mr-4 flex">
            <a className="mr-6 flex items-center space-x-2" href="/">
              <span className="font-bold sm:inline-block">
                DeFAI Assistant
              </span>
            </a>
          </div>
          <div className="flex flex-1 items-center space-x-2 justify-end">
            <Button
              variant={isConnected ? "outline" : "default"}
              onClick={isConnected ? disconnectWallet : connectWallet}
              className="relative"
            >
              <Wallet className="mr-2 h-4 w-4" />
              {isConnected ? (
                <span>
                  {account?.slice(0, 6)}...{account?.slice(-4)}
                </span>
              ) : (
                "Connect Wallet"
              )}
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <div className="flex flex-col gap-8">
          <div className="flex flex-col items-center text-center space-y-4">
            <h1 className="text-3xl font-bold leading-tight tracking-tighter md:text-5xl lg:leading-[1.1]">
              Welcome to DeFAI Assistant
            </h1>
            <p className="max-w-[750px] text-lg text-muted-foreground sm:text-xl">
              Your AI-powered DeFi companion. Connect your wallet to get started.
            </p>
          </div>
          <Features />
        </div>
      </main>
    </div>
  );
} 