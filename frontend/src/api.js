const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const endpoints = {
  health: "/health",
  query: "/api/v1/query",
  transcribe: "/api/v1/transcribe",
};


async function request(
  path,
  options = {}
) {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers: {
        ...(options.body instanceof FormData
          ? {}
          : {
              "Content-Type":
                "application/json",
            }),
        ...(options.headers || {}),
      },
    }
  );

  const contentType =
    response.headers.get(
      "content-type"
    ) || "";

  const payload =
    contentType.includes(
      "application/json"
    )
      ? await response.json()
      : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object" &&
      payload?.detail
        ? payload.detail
        : `Request failed with HTTP ${response.status}`;

    throw new Error(message);
  }

  return payload;
}


export async function checkHealth() {
  return request(
    endpoints.health
  );
}


export async function transcribeAudio(
  blob,
  deviceId
) {
  const form = new FormData();

  form.append(
    "audio",
    blob,
    "voice.webm"
  );

  if (deviceId) {
    form.append(
      "device_id",
      deviceId
    );
  }

  return request(
    endpoints.transcribe,
    {
      method: "POST",
      body: form,
    }
  );
}


export async function askRag(
  question
) {
  return request(
    endpoints.query,
    {
      method: "POST",
      body: JSON.stringify({
        query: question,
      }),
    }
  );
}


export {
  API_BASE_URL,
  endpoints,
};