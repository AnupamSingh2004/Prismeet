// Google Identity Services type definitions
interface GoogleAccountsId {
    initialize(config: {
        client_id: string;
        callback: (response: GoogleCredentialResponse) => void;
    }): void;
    renderButton(element: HTMLElement, config: {
        theme?: string;
        size?: string;
        width?: string;
        text?: string;
    }): void;
    prompt(): void;
}

interface GoogleAccounts {
    id: GoogleAccountsId;
}

interface GoogleGsi {
    accounts: GoogleAccounts;
}

declare global {
    interface Window {
        google: GoogleGsi;
    }
}

export interface GoogleCredentialResponse {
    credential: string;
    select_by: string;
}

export class GoogleAuth {
    private static clientId: string;
    private static isLoaded = false;

    static initialize(clientId: string): Promise<void> {
        this.clientId = clientId;

        return new Promise((resolve, reject) => {
            if (this.isLoaded) {
                resolve();
                return;
            }

            // Load Google Identity Services script
            const script = document.createElement('script');
            script.src = 'https://accounts.google.com/gsi/client';
            script.async = true;
            script.defer = true;

            script.onload = () => {
                this.isLoaded = true;
                resolve();
            };

            script.onerror = () => {
                reject(new Error('Failed to load Google Identity Services'));
            };

            document.head.appendChild(script);
        });
    }

    static renderButton(element: HTMLElement, callback: (token: string) => void): void {
        if (!this.isLoaded || !window.google) {
            throw new Error('Google Identity Services not loaded');
        }

        window.google.accounts.id.initialize({
            client_id: this.clientId,
            callback: (response: GoogleCredentialResponse) => {
                callback(response.credential);
            },
        });

        window.google.accounts.id.renderButton(element, {
            theme: 'outline',
            size: 'large',
            width: '100%',
            text: 'continue_with',
        });
    }

    static showOneTap(callback: (token: string) => void): void {
        if (!this.isLoaded || !window.google) {
            throw new Error('Google Identity Services not loaded');
        }

        window.google.accounts.id.initialize({
            client_id: this.clientId,
            callback: (response: GoogleCredentialResponse) => {
                callback(response.credential);
            },
        });

        window.google.accounts.id.prompt();
    }
}