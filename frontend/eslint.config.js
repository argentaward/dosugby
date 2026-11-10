import js from '@eslint/js'
import prettier from 'eslint-config-prettier'
import boundaries from 'eslint-plugin-boundaries'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import globals from 'globals'
import tseslint from 'typescript-eslint'

/**
 * Слои Feature-Sliced Design (сверху вниз):
 * app -> pages -> widgets -> features -> entities -> shared
 *
 * Правило: слой может импортировать только нижележащие слои.
 */
const FSD_LAYERS = [
  { type: 'app', pattern: 'src/app/**' },
  { type: 'pages', pattern: 'src/pages/*', capture: ['slice'] },
  { type: 'widgets', pattern: 'src/widgets/*', capture: ['slice'] },
  { type: 'features', pattern: 'src/features/*', capture: ['slice'] },
  { type: 'entities', pattern: 'src/entities/*', capture: ['slice'] },
  { type: 'shared', pattern: 'src/shared/**' },
]

const allowTargets = (types) => types.map((type) => ({ to: { element: { type } } }))

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'src/shared/api/schema.gen.ts'] },
  js.configs.recommended,
  ...tseslint.configs.strict,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      boundaries,
    },
    settings: {
      'boundaries/include': ['src/**/*'],
      'boundaries/elements': FSD_LAYERS,
      'import/resolver': {
        typescript: {
          alwaysTryTypes: true,
          project: './tsconfig.json',
        },
      },
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      'no-console': 'error',
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports' }],
      'boundaries/dependencies': [
        'error',
        {
          default: 'disallow',
          policies: [
            {
              from: { element: { type: 'app' } },
              allow: allowTargets(['pages', 'widgets', 'features', 'entities', 'shared']),
            },
            {
              from: { element: { type: 'pages' } },
              allow: allowTargets(['widgets', 'features', 'entities', 'shared']),
            },
            {
              from: { element: { type: 'widgets' } },
              allow: allowTargets(['features', 'entities', 'shared']),
            },
            {
              from: { element: { type: 'features' } },
              allow: allowTargets(['entities', 'shared']),
            },
            {
              from: { element: { type: 'entities' } },
              allow: allowTargets(['shared']),
            },
            {
              from: { element: { type: 'shared' } },
              allow: allowTargets(['shared']),
            },
          ],
        },
      ],
    },
  },
  prettier,
)
