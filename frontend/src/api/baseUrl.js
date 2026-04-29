export function getApiBaseUrl() {
    const configuredUrl = process.env.VUE_APP_API_URL

    if (configuredUrl) {
        return configuredUrl.replace(/\/+$/, "")
    }

    return ""
}
