export async function textToSpeech(text: string, serverUrl: string): Promise<ArrayBuffer> {
    if (!serverUrl) {
        throw new Error("Liquid Audio server URL is not set.");
    }
    
    try {
        const response = await fetch(serverUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                model: "LFM2-Audio-1.5B", // Specify model for clarity, server might use it
            }),
        });

        if (!response.ok) {
            const errorBody = await response.text();
            console.error("Local TTS API Error:", errorBody);
            throw new Error(`Failed to generate speech from local server. Status: ${response.status}`);
        }

        const audioData = await response.arrayBuffer();
        return audioData;

    } catch (error) {
        console.error("Error calling local TTS API:", error);
        throw error;
    }
}
