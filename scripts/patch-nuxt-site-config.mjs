import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const cwd = process.cwd()
const candidateRoots = [
  join(cwd, 'node_modules', '.pnpm'),
  join(cwd, '.nuxt', 'dist', 'server', 'node_modules', '.pnpm'),
]

const shim = `const appBaseURL = process.env.NUXT_APP_BASE_URL || process.env.NITRO_APP_BASE_URL || '/'
const appBuildAssetsDir = process.env.NUXT_APP_BUILD_ASSETS_DIR || '/_nuxt/'
const appCdnURL = process.env.NUXT_APP_CDN_URL || ''

function joinRelativeURL(...parts) {
  return parts
    .filter((part) => part !== undefined && part !== null && part !== '')
    .map((part, index) => {
      const value = String(part)
      if (index === 0) {
        return value.replace(/\\/+$/g, '')
      }
      return value.replace(/^\\/+|\\/+$/g, '')
    })
    .join('/')
    .replace(/^(https?:)\\/([^/])/, '$1//$2')
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
`

let patched = 0

function patchPackage(packageDir, label) {
  const packagePath = join(packageDir, 'package.json')
  const packageJson = existsSync(packagePath)
    ? JSON.parse(readFileSync(packagePath, 'utf8'))
    : {
        name: label,
        type: 'module',
      }

  packageJson.imports = {
    ...(packageJson.imports || {}),
    '#internal/nuxt/paths': './nuxt-internal-paths.mjs',
  }

  writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`)
  writeFileSync(join(packageDir, 'nuxt-internal-paths.mjs'), shim)
  patched += 1
  console.log(`Patched ${label} internal path imports.`)
}

for (const root of candidateRoots) {
  if (!existsSync(root)) {
    continue
  }

  for (const entry of readdirSync(root)) {
    if (entry.startsWith('nuxt-site-config@') || entry.startsWith('nuxt-site-config_')) {
      patchPackage(join(root, entry, 'node_modules', 'nuxt-site-config'), 'nuxt-site-config')
    }
    if (entry.startsWith('nuxt@') || entry.startsWith('nuxt_')) {
      patchPackage(join(root, entry, 'node_modules', 'nuxt'), 'nuxt')
    }
  }
}

if (patched > 0) {
  console.log(`Patched Nuxt internal path imports in ${patched} package scope(s).`)
}
