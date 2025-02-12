import { Web3Provider } from "@/context/Web3Context";
import { DialogProvider } from "@/context/DialogContext";
import { AuthorizersProvider } from "@/context/AuthorizersContext";
import { Toaster } from "@/components/ui/toaster";
import Layout from "@/components/Layout";

function App() {
  return (
    <AuthorizersProvider>
      <Web3Provider>
        <DialogProvider>
          <Layout />
          <Toaster />
        </DialogProvider>
      </Web3Provider>
    </AuthorizersProvider>
  );
}

export default App;