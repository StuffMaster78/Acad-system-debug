const appBaseURL = process.env.NUXT_APP_BASE_URL || process.env.NITRO_APP_BASE_URL || '/'
const appBuildAssetsDir = process.env.NUXT_APP_BUILD_ASSETS_DIR || '/_nuxt/'
const appCdnURL = process.env.NUXT_APP_CDN_URL || ''

function joinRelativeURL(...parts) {
  return parts
    .filter((part) => part !== undefined && part !== null && part !== '')
    .map((part, index) => {
      const value = String(part)
      if (index === 0) {
        return value.replace(/\/+$/g, '')
      }
      return value.replace(/^\/+|\/+$/g, '')
    })
    .join('/')
    .replace(/^(https?:)\/([^/])/, '$1//$2')
}

export function baseURL() {
  return appBaseURL
}

export function buildAssetsDir() {
  return appBuildAssetsDir
}

export function publicAssetsURL(...path) {
  const publicBase = appCdnURL || appBaseURL
  return path.length ? joinRelativeURL(publicBase, ...path) : publicBase
}

export function buildAssetsURL(...path) {
  return joinRelativeURL(publicAssetsURL(), buildAssetsDir(), ...path)
}
