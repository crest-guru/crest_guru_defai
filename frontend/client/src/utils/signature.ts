import { SignaturePayload } from '../../../shared/types';

export const SIGNATURE_MESSAGE = "Welcome to our app! Sign this message to verify your wallet ownership. Timestamp:";

export async function createSignaturePayload(address: string, signer: any): Promise<SignaturePayload> {
  const timestamp = Date.now();
  const message = `${SIGNATURE_MESSAGE} ${timestamp}`;
  const signature = await signer.signMessage(message);
  
  return {
    address,
    message,
    signature,
    timestamp
  };
} 