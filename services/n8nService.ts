import { ConnectionSettings, N8NWorkflow } from '../types';

export interface N8NExecutionResult {
    success: boolean;
    data?: any;
    error?: string;
    executionId?: string;
}

export class N8NService {
    private baseUrl: string;
    private apiKey: string;

    constructor(settings: ConnectionSettings) {
        this.baseUrl = settings.n8nUrl;
        this.apiKey = settings.n8nApiKey;
    }

    /**
     * Test connection to N8N API
     */
    async testConnection(): Promise<N8NExecutionResult> {
        try {
            const response = await this.makeRequest('/api/v1/workflows');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: this.formatErrorMessage(error)
            };
        }
    }

    /**
     * Fetch available workflows from N8N
     */
    async fetchWorkflows(): Promise<N8NWorkflow[]> {
        try {
            const response = await this.makeRequest('/api/v1/workflows');
            return response.data.map((wf: any) => ({
                id: wf.id,
                name: wf.name
            }));
        } catch (error) {
            console.error('Failed to fetch N8N workflows:', error);
            throw new Error(this.formatErrorMessage(error));
        }
    }

    /**
     * Execute a workflow by name
     */
    async executeWorkflow(workflowName: string, data?: any): Promise<N8NExecutionResult> {
        try {
            // First, get the workflow by name to find its ID
            const workflows = await this.fetchWorkflows();
            const workflow = workflows.find(wf => wf.name === workflowName);

            if (!workflow) {
                return {
                    success: false,
                    error: `Workflow "${workflowName}" not found. Available workflows: ${workflows.map(w => w.name).join(', ')}`
                };
            }

            // Execute the workflow
            const executionData = {
                workflowId: workflow.id,
                data: data || {}
            };

            const response = await this.makeRequest('/api/v1/workflows/execute', {
                method: 'POST',
                body: JSON.stringify(executionData)
            });

            return {
                success: true,
                data: response,
                executionId: response.data?.executionId
            };
        } catch (error) {
            return {
                success: false,
                error: this.formatErrorMessage(error)
            };
        }
    }

    /**
     * Get execution status
     */
    async getExecutionStatus(executionId: string): Promise<N8NExecutionResult> {
        try {
            const response = await this.makeRequest(`/api/v1/executions/${executionId}`);
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: this.formatErrorMessage(error)
            };
        }
    }

    /**
     * Make authenticated requests to N8N API
     */
    private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultHeaders = {
            'Content-Type': 'application/json',
            'X-N8N-API-KEY': this.apiKey,
        };

        const config: RequestInit = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            return await response.json();
        } catch (error) {
            // Enhance error messages for better debugging
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                throw new Error('CORS Policy Error: N8N server is not configured to accept requests from this origin. Please restart N8N with CORS configuration.');
            }
            throw error;
        }
    }

    /**
     * Format error messages for better user experience
     */
    private formatErrorMessage(error: unknown): string {
        if (error instanceof Error) {
            if (error.message.includes('401')) {
                return '❌ Authentication Failed: Invalid N8N API Key. Please check your API key in N8N Settings > API.';
            } else if (error.message.includes('403')) {
                return '❌ Forbidden: Insufficient permissions to access N8N API.';
            } else if (error.message.includes('404')) {
                return '❌ N8N API Not Found: Make sure N8N is running and the URL is correct (default: http://localhost:5678).';
            } else if (error.message.includes('CORS')) {
                return '🔒 CORS Policy Error: Please restart N8N with CORS configuration enabled. Run "fix-cors.bat" (Windows) or "./fix-cors.sh" (Linux/Mac).';
            } else if (error.message.includes('ECONNREFUSED')) {
                return '❌ Connection Refused: N8N is not running or not accessible at the specified URL.';
            } else if (error.message.includes('ENOTFOUND')) {
                return '❌ Host Not Found: N8N URL is incorrect or DNS resolution failed.';
            } else {
                return `❌ Error: ${error.message}`;
            }
        }
        return '❌ An unknown error occurred while connecting to N8N.';
    }

    /**
     * Validate N8N connection settings
     */
    static validateSettings(settings: ConnectionSettings): { isValid: boolean; errors: string[] } {
        const errors: string[] = [];

        if (!settings.n8nUrl) {
            errors.push('N8N URL is required');
        } else {
            try {
                new URL(settings.n8nUrl);
            } catch {
                errors.push('N8N URL is not a valid URL');
            }
        }

        if (!settings.n8nApiKey) {
            errors.push('N8N API Key is required');
        } else if (settings.n8nApiKey.length < 10) {
            errors.push('N8N API Key appears to be too short');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

/**
 * Helper function to create and configure N8N service
 */
export function createN8NService(settings: ConnectionSettings): N8NService {
    const validation = N8NService.validateSettings(settings);
    if (!validation.isValid) {
        throw new Error(`Invalid N8N configuration: ${validation.errors.join(', ')}`);
    }

    return new N8NService(settings);
}