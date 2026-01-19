module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2021: true,
  },
  extends: [
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
  },
  rules: {
    // Suppress false positive warnings about bg-gradient-to-br
    // bg-gradient-to-br is the correct Tailwind CSS class
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    // Vue 3 supports v-model arguments (e.g., v-model:visible, v-model:show)
    'vue/no-v-model-argument': 'off',
  },
  ignorePatterns: [
    'dist/',
    'node_modules/',
    'coverage/',
  ],
};

