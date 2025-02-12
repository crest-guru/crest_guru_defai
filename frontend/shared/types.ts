export interface SignaturePayload {
  address: string;
  message: string;
  signature: string;
  timestamp: number;
}

export interface WalletCreateRequest {
  address: string;
  signature: string;
  message: string;
  timestamp: number;
} 