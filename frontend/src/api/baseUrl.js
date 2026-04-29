const FALLBACK_API_URL = "http://127.0.0.1:8000"

function normalizeBaseUrl(url) {
    return url.replace(/\/+$/, "")
}

export function getApiBaseUrl() {
    const configuredUrl = process.env.VUE_APP_API_URL

    if (configuredUrl) {
        return normalizeBaseUrl(configuredUrl)
    }

    if (typeof window !== "undefined" && window.location?.origin) {
        return normalizeBaseUrl(window.location.origin)
    }

    return FALLBACK_API_URL
}
